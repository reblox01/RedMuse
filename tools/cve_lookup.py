#!/usr/bin/env python3
"""CVE lookup for RedMuse runs. Standard library only, no API keys.

Reads a JSON list of fingerprint items from a file or stdin and writes
a JSON shortlist to stdout. Two item kinds:

  package: {"kind": "package", "ecosystem": "npm",
            "package": "lodash", "version": "4.17.20"}
  product: {"kind": "product", "product": "PHP", "version": "8.1.0"}

Package items query the OSV API (no key). OSV returns affected ranges
with introduced and fixed events, so applicability is computed here:
a version at or above introduced and below fixed is applicable, a
version at or above fixed is not applicable, a version below
introduced is not applicable. Unfixed ranges (no fixed event) are
applicable from introduced onward. Versions that are not plain
numeric dot versions get applicability "needs-confirmation" instead
of a computed answer.

Product items (runtimes, servers, frameworks without an OSV
ecosystem) query the NVD API keyword search (no key, rate limited).
NVD keyword results are candidates only, never auto-confirmed: the
agent must confirm the product and version range from the returned
configuration before any probe is selected. A 403 or 429 from NVD
is recorded as an error and the run continues, it never fails the
whole lookup.

The tool never contains a list of vulnerability ids. Every result
comes from a live query at run time. If a source is unreachable,
the output records the error and the run must say "CVE check
incomplete" in its report, never "no known vulnerabilities".

Exit code 0 means the tool ran, even when individual queries
failed (those failures are in the errors list). Exit code 2
means the input itself was unusable.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

OSV_URL = "https://api.osv.dev/v1/query"
NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
TIMEOUT = 20
TIMEOUT_NVD = 60
USER_AGENT = "RedMuse-cve-lookup"

_OPENER = None


def _opener():
    """Opener that honours proxy env vars, including proxy auth.

    Plain urlopen does not reliably send proxy credentials, which
    makes proxied HTTPS hang instead of failing fast. Building the
    opener explicitly, with credentials taken from the proxy URL
    itself and never printed or logged, fixes that on proxied
    machines and changes nothing on direct machines.
    """
    global _OPENER
    if _OPENER is not None:
        return _OPENER
    proxy_handler = urllib.request.ProxyHandler()
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    for scheme in ("https", "http"):
        proxy_url = urllib.request.getproxies().get(scheme, "")
        if not proxy_url:
            continue
        parsed = urllib.parse.urlparse(proxy_url)
        if parsed.username:
            password_mgr.add_password(
                None, parsed.netloc,
                urllib.parse.unquote(parsed.username),
                urllib.parse.unquote(parsed.password or ""),
            )
    _OPENER = urllib.request.build_opener(
        proxy_handler,
        urllib.request.ProxyBasicAuthHandler(password_mgr),
    )
    return _OPENER

# CWE to exploit class, heuristic only. The agent confirms the class
# from the vulnerability description before selecting a probe. This
# map contains no vulnerability ids, only generic weakness classes.
CWE_CLASS = {
    "79": "xss",
    "87": "xss",
    "89": "sql-injection",
    "78": "rce",
    "94": "rce",
    "95": "rce",
    "22": "path-traversal",
    "287": "auth-bypass",
    "862": "auth-bypass",
    "863": "auth-bypass",
    "200": "info-disclosure",
    "400": "dos",
    "770": "dos",
}

KEYWORD_CLASS = [
    ("cross-site scripting", "xss"),
    ("sql injection", "sql-injection"),
    ("remote code execution", "rce"),
    ("command injection", "rce"),
    ("code injection", "rce"),
    ("code execution", "rce"),
    ("authentication bypass", "auth-bypass"),
    ("bypass authentication", "auth-bypass"),
    ("directory traversal", "path-traversal"),
    ("path traversal", "path-traversal"),
    ("denial of service", "dos"),
    ("information disclosure", "info-disclosure"),
]


def parse_version(text):
    """Return a numeric tuple for plain dot versions, else None."""
    if not isinstance(text, str):
        return None
    text = text.strip().lstrip("v")
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)*", text):
        return None
    return tuple(int(p) for p in text.split("."))


def cmp_version(a, b):
    """Compare numeric version tuples, padding shorter with zeros."""
    n = max(len(a), len(b))
    a = a + (0,) * (n - len(a))
    b = b + (0,) * (n - len(b))
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def suggest_class(summary, details, cwe_list):
    for cwe in cwe_list or []:
        m = re.search(r"(\d+)", str(cwe))
        if m and m.group(1) in CWE_CLASS:
            return CWE_CLASS[m.group(1)]
    text = ((summary or "") + " " + (details or "")).lower()
    for keyword, cls in KEYWORD_CLASS:
        if keyword in text:
            return cls
    return "other"


def osv_query(item):
    """Query OSV for one package item. Returns (results, error)."""
    body = json.dumps(
        {
            "package": {"name": item["package"], "ecosystem": item["ecosystem"]},
            "version": item["version"],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        OSV_URL,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    try:
        with _opener().open(req, timeout=TIMEOUT) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        return [], "osv http %s for %s %s" % (
            exc.code, item["ecosystem"], item["package"])
    except Exception as exc:  # network down, timeout, bad JSON
        return [], "osv error for %s %s: %s" % (
            item["ecosystem"], item["package"], exc)
    version = parse_version(item["version"])
    results = []
    for vuln in data.get("vulns", []):
        vid = vuln.get("id", "")
        aliases = vuln.get("aliases", [])
        summary = vuln.get("summary") or vuln.get("details", "")[:200]
        details = vuln.get("details", "")
        severity = None
        score = None
        for sev in vuln.get("severity", []):
            if sev.get("type", "").startswith("CVSS"):
                score = sev.get("score")
                severity = sev.get("type")
                break
        cwe_list = []
        db_specific = vuln.get("database_specific", {}) or {}
        for cwe in db_specific.get("cwe", []) or []:
            cwe_list.append(str(cwe))
        fixed_version = None
        applicable = None
        for affected in vuln.get("affected", []):
            for rng in affected.get("ranges", []):
                introduced = None
                fixed = None
                for event in rng.get("events", []):
                    if "introduced" in event:
                        introduced = event["introduced"]
                    if "fixed" in event:
                        fixed = event["fixed"]
                if fixed:
                    fixed_version = fixed
                if version is None:
                    applicable = "needs-confirmation"
                    continue
                intro_v = parse_version(introduced) if introduced else None
                fixed_v = parse_version(fixed) if fixed else None
                if intro_v is not None and cmp_version(version, intro_v) < 0:
                    applicable = "not-applicable"
                elif fixed_v is not None and cmp_version(version, fixed_v) >= 0:
                    applicable = "not-applicable"
                elif fixed_v is not None:
                    applicable = "applicable"
                elif intro_v is not None:
                    applicable = "applicable"
        if applicable is None:
            applicable = "needs-confirmation"
        results.append(
            {
                "input": item,
                "source": "osv",
                "vuln_id": vid,
                "aliases": aliases,
                "summary": summary,
                "severity": severity,
                "cvss_score": score,
                "cwe": cwe_list,
                "exploit_class_suggested": suggest_class(
                    summary, details, cwe_list),
                "fixed_version": fixed_version,
                "applicability": applicable,
            }
        )
    return results, None


def nvd_query(item):
    """Query NVD keyword search for one product item. Candidates only."""
    from urllib.parse import quote

    url = "%s?keywordSearch=%s&resultsPerPage=10" % (
        NVD_URL, quote(item["product"]))
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with _opener().open(req, timeout=TIMEOUT_NVD) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        return [], "nvd http %s for %s" % (exc.code, item["product"])
    except Exception as exc:
        return [], "nvd error for %s: %s" % (item["product"], exc)
    results = []
    for entry in data.get("vulnerabilities", []):
        cve = entry.get("cve", {})
        vid = cve.get("id", "")
        descriptions = cve.get("descriptions", [])
        summary = ""
        for desc in descriptions:
            if desc.get("lang") == "en":
                summary = desc.get("value", "")
                break
        score = None
        severity = None
        for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            metrics = cve.get("metrics", {}).get(key, [])
            if metrics:
                cvss = metrics[0].get("cvssData", {})
                score = cvss.get("baseScore")
                severity = cvss.get("baseSeverity")
                break
        weaknesses = cve.get("weaknesses", [])
        cwe_list = []
        for weak in weaknesses:
            for desc in weak.get("description", []):
                cwe_list.append(desc.get("value", ""))
        configs = []
        for config in cve.get("configurations", []):
            for node in config.get("nodes", []):
                for match in node.get("cpeMatch", []):
                    configs.append(
                        {
                            "criteria": match.get("criteria", ""),
                            "version_start": (
                                match.get("versionStartIncluding")
                                or match.get("versionStartExcluding")
                            ),
                            "version_end": (
                                match.get("versionEndIncluding")
                                or match.get("versionEndExcluding")
                            ),
                        }
                    )
        version_match = False
        queried = parse_version(item["version"])
        if queried is not None:
            for cfg in configs:
                start_v = parse_version(cfg["version_start"]) \
                    if cfg["version_start"] else None
                end_v = parse_version(cfg["version_end"]) \
                    if cfg["version_end"] else None
                if start_v is not None and cmp_version(queried, start_v) < 0:
                    continue
                if end_v is not None and cmp_version(queried, end_v) > 0:
                    continue
                if start_v is not None or end_v is not None:
                    version_match = True
                    break
        results.append(
            {
                "input": item,
                "source": "nvd",
                "vuln_id": vid,
                "aliases": [],
                "summary": summary[:300],
                "severity": severity,
                "cvss_score": score,
                "cwe": cwe_list,
                "exploit_class_suggested": suggest_class(
                    summary, "", cwe_list),
                "fixed_version": None,
                "applicability": "needs-confirmation",
                "version_match": version_match,
                "configurations": configs[:5],
            }
        )
    return results, None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Look up known vulnerabilities for fingerprinted "
        "packages and products. Reads JSON from a file or stdin.")
    parser.add_argument("--input", help="JSON file, else stdin")
    parser.add_argument(
        "--osv-only", action="store_true",
        help="Skip NVD product queries, OSV package queries only")
    args = parser.parse_args(argv)

    try:
        if args.input:
            with open(args.input, "r", encoding="utf-8") as fh:
                items = json.load(fh)
        else:
            items = json.load(sys.stdin)
    except Exception as exc:
        print("unusable input: %s" % exc, file=sys.stderr)
        return 2
    if not isinstance(items, list):
        print("unusable input: expected a JSON list", file=sys.stderr)
        return 2

    results = []
    errors = []
    osv_status = "ok"
    nvd_status = "skipped" if args.osv_only else "ok"
    for item in items:
        if not isinstance(item, dict):
            errors.append("skipped non-object item")
            continue
        kind = item.get("kind")
        if kind == "package":
            if not all(k in item for k in ("ecosystem", "package", "version")):
                errors.append("package item missing ecosystem, package, "
                              "or version: %r" % (item,))
                continue
            res, err = osv_query(item)
            results.extend(res)
            if err:
                errors.append(err)
                osv_status = "error"
        elif kind == "product":
            if args.osv_only:
                continue
            if not all(k in item for k in ("product", "version")):
                errors.append("product item missing product or version: "
                              "%r" % (item,))
                continue
            res, err = nvd_query(item)
            results.extend(res)
            if err:
                errors.append(err)
                nvd_status = "error"
        else:
            errors.append("unknown kind %r, expected package or product"
                          % (kind,))
    output = {
        "tool": "cve_lookup",
        "osv": osv_status,
        "nvd": nvd_status,
        "results": results,
        "errors": errors,
    }
    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
