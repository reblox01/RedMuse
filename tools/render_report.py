#!/usr/bin/env python3
"""Render a redmuse findings.json as a standalone HTML report.

Standard library only. No JavaScript, no external assets, inline CSS.

The renderer enforces never-report-clean, it does not just print
the supplied outcome. A clean verdict renders only for a run
that declares complete coverage and has zero findings. A run
that declares partial coverage, or that supplies no coverage
statement at all, renders as partial or unknown, never as
clean. A supplied clean verdict that contradicts the findings
or the coverage is refused: no file is written, exit code 2.

Accepted input is the object shape tools/findings.py exports:
findings, counts, target, mode, outcome, and optionally a
coverage object with a complete flag and a classes_not_probed
list. A bare JSON array (the old export shape) still renders,
as an unknown-outcome run, never as clean.

Usage:
  python3 tools/render_report.py findings.json report.html [--title TITLE]
"""
import html
import json
import sys

COLORS = {
    "critical": "#b42318",
    "high": "#dc6803",
    "medium": "#b54708",
    "low": "#067647",
    "info": "#175cd3",
}

ORDER = ["critical", "high", "medium", "low", "info"]

CLEAN_WORDS = {"clean", "no findings", "no-findings", "no findings found"}


def card(f):
    sev = f.get("severity", "info")
    color = COLORS.get(sev, "#333")
    cwe = f.get("cwe")
    cwe_line = f"<p><b>CWE:</b> {html.escape(str(cwe))}</p>" if cwe else ""
    endpoint = html.escape(str(f.get("endpoint", "")))
    param = f.get("parameter")
    param_line = (
        f"<p><b>Parameter:</b> {html.escape(str(param))}</p>" if param else ""
    )
    return (
        f'<div class="card"><span class="sev" style="background:{color}">'
        f"{html.escape(sev)}</span>"
        f"<h2>{html.escape(str(f.get('title', '')))}</h2>"
        f"<p><b>Endpoint:</b> {endpoint}</p>{param_line}{cwe_line}"
        f"<p><b>Proof:</b> {html.escape(str(f.get('proof', '')))}</p>"
        f"<p><b>Fix:</b> {html.escape(str(f.get('fix', '')))}</p></div>"
    )


def coverage_complete(data):
    """True only when the run declares its coverage complete.

    A coverage object with a complete flag decides. Without one,
    an outcome of complete declares it; anything else (partial,
    clean, missing, unknown) does not, because a clean verdict
    needs an explicit complete-coverage statement behind it.
    """
    cov = data.get("coverage")
    if isinstance(cov, dict):
        if "complete" in cov:
            return bool(cov["complete"])
        if cov.get("classes_not_probed"):
            return False
    return str(data.get("outcome", "")).strip().lower() == "complete"


def validate(data, findings):
    """Check outcome against findings and coverage. Return an error string, or None.

    Refusals, before any file is written:
    - a clean verdict with findings present contradicts itself.
    - a clean verdict without declared complete coverage is unverified.
    - an outcome of complete with a coverage object that says
      incomplete contradicts itself.
    """
    outcome = str(data.get("outcome", "")).strip().lower()
    complete = coverage_complete(data)
    if outcome in CLEAN_WORDS:
        if findings:
            return ("refusing to render: outcome claims clean but "
                    f"{len(findings)} finding(s) are present")
        if not complete:
            return ("refusing to render: outcome claims clean but "
                    "coverage is not declared complete")
    if outcome == "complete" and isinstance(data.get("coverage"), dict):
        if data["coverage"].get("complete") is False:
            return ("refusing to render: outcome claims complete but "
                    "the coverage statement says incomplete")
    return None


def outcome_banner(data, findings):
    """Displayed outcome and honesty banner. Partial or unknown runs never read as clean."""
    outcome = str(data.get("outcome", "")).strip().lower()
    if outcome == "partial":
        return ("partial (not clean)",
                "Partial run: untested classes are not clean. "
                "This report makes no clean claim.")
    if outcome in CLEAN_WORDS:
        return ("clean",
                "Clean verdict: complete run, no findings on the "
                "probed surface.")
    if outcome == "complete":
        return ("complete", "")
    return ("not declared",
            "Outcome not declared: this report makes no clean claim. "
            "Coverage is unknown, so untested classes are not clean.")


def main():
    if len(sys.argv) < 3:
        print("usage: render_report.py findings.json report.html [--title TITLE]")
        return 1
    findings_path, out_path = sys.argv[1], sys.argv[2]
    title = "RedMuse report"
    if "--title" in sys.argv:
        title = sys.argv[sys.argv.index("--title") + 1]
    with open(findings_path) as fh:
        data = json.load(fh)
    if isinstance(data, list):
        # Legacy bare-array export: findings with no coverage statement.
        data = {"findings": data, "counts": {}, "target": "",
                "mode": "", "outcome": ""}
    if not isinstance(data, dict) or "findings" not in data:
        print("refusing to render: input has no findings list", file=sys.stderr)
        return 2
    findings = sorted(
        data.get("findings", []),
        key=lambda f: ORDER.index(f.get("severity", "info")),
    )
    error = validate(data, findings)
    if error:
        print(error, file=sys.stderr)
        return 2
    counts = {sev: 0 for sev in ORDER}
    for f in findings:
        counts[f.get("severity", "info")] = counts.get(f.get("severity", "info"), 0) + 1
    chips = " ".join(
        f'<span class="chip">{sev}: {counts.get(sev, 0)}</span>'
        for sev in ORDER
    )
    cards = "\n".join(card(f) for f in findings)
    target = html.escape(str(data.get("target", "")))
    mode = html.escape(str(data.get("mode", "")))
    outcome_text, banner = outcome_banner(data, findings)
    banner_html = f"<p><b>{html.escape(banner)}</b></p>" if banner else ""
    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:900px;margin:40px auto;
padding:0 20px;color:#1d2939}}
.card{{border:1px solid #d0d5dd;border-radius:12px;padding:20px;
margin:20px 0}} .sev{{color:#fff;padding:4px 12px;border-radius:20px;
font-size:13px;text-transform:uppercase}}
.chip{{display:inline-block;border:1px solid #d0d5dd;border-radius:20px;
padding:4px 12px;margin:2px}} h1{{font-size:28px}} h2{{margin-top:12px}}
</style></head><body>
<h1>{html.escape(title)}</h1>
<p><b>Target:</b> {target} | <b>Mode:</b> {mode} | <b>Outcome:</b> {html.escape(outcome_text)}</p>
{banner_html}
<p>{chips}</p>
{cards}
<p><i>Generated by RedMuse. A finding without a reproduced proof is
unvalidated. A clean report covers only the probed surface.</i></p>
</body></html>
"""
    with open(out_path, "w") as fh:
        fh.write(page)
    print(f"wrote {out_path} ({len(findings)} findings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
