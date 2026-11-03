#!/usr/bin/env python3
"""RedMuse update check. Prints one line per tracked source:

    name | local | latest | status

Sources come from skills/redmuse-update/sources.yaml, which is the
single source of truth. This script contains no hardcoded source
URLs: adding a source to that file is enough to have it checked.

Statuses: up-to-date, update-available, ahead, diverged,
unknown-relation, unreachable, manual-review-if-changed, manual,
skipped. This script never rewrites skill content and never pushes.
A fast-forward pull of RedMuse itself is a separate step the
orchestrator takes after seeing update-available.

Usage: ./tools/check_updates.py [repo-dir]
Requires: python3 (standard library only) and git.
"""

import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def parse_sources(path):
    """Parse the strict subset of YAML used by sources.yaml.

    Supported lines only: a top-level 'sources:' line, '  - name: X'
    item lines, '    key: value' lines, a '    covers:' line, and
    '      - item' lines under it. Anything else fails loudly
    instead of being silently misread.
    """
    sources = []
    current = None
    in_covers = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if raw == "sources:":
            continue
        if raw.startswith("  - name: "):
            current = {"covers": []}
            current["name"] = raw.split(":", 1)[1].strip()
            sources.append(current)
            in_covers = False
            continue
        if current is None:
            raise ValueError("unexpected line before first source: %r" % raw)
        if raw == "    covers:":
            in_covers = True
            continue
        if in_covers and raw.startswith("      - "):
            current["covers"].append(raw.split("-", 1)[1].strip())
            continue
        if raw.startswith("    ") and ":" in raw:
            in_covers = False
            key, value = raw.strip().split(":", 1)
            current[key.strip()] = value.strip()
            continue
        raise ValueError("unsupported line in sources.yaml: %r" % raw)
    for source in sources:
        for required in ("name", "kind", "check", "auto_update"):
            if required not in source:
                raise ValueError(
                    "source %s is missing %s" % (source.get("name"), required)
                )
    return sources


def ls_remote_head(repo):
    out, code = run(["git", "ls-remote", repo, "HEAD"])
    if code != 0 or not out:
        return ""
    return out.split()[0]


def check_self(root, source):
    out, code = run(["git", "-C", str(root), "rev-parse", "--git-dir"])
    if code != 0:
        return "%s | unknown | unknown | skipped (not a git checkout)" % source["name"]
    local, _ = run(["git", "-C", str(root), "rev-parse", "HEAD"])
    fetch_ok = run(["git", "-C", str(root), "fetch", "-q", "origin"])[1] == 0
    if fetch_ok:
        remote, _ = run(["git", "-C", str(root), "rev-parse", "origin/main"])
    else:
        remote = ls_remote_head(source["repo"])
    name = source["name"]
    if not remote:
        return "%s | %s | unknown | unreachable" % (name, local)
    if local == remote:
        return "%s | %s | %s | up-to-date" % (name, local, remote)
    if fetch_ok:
        if run(["git", "-C", str(root), "merge-base", "--is-ancestor", local, remote])[1] == 0:
            return "%s | %s | %s | update-available" % (name, local, remote)
        if run(["git", "-C", str(root), "merge-base", "--is-ancestor", remote, local])[1] == 0:
            return "%s | %s | %s | ahead (unpushed commits, pull is a no-op)" % (
                name,
                local,
                remote,
            )
        return "%s | %s | %s | diverged (stop, do not force)" % (name, local, remote)
    return "%s | %s | %s | unknown-relation (fetch failed, pull manually)" % (
        name,
        local,
        remote,
    )


def check_reference(source):
    latest = ls_remote_head(source["repo"])
    if not latest:
        return "%s | reference-only | unknown | unreachable" % source["name"]
    return "%s | reference-only | %s | manual-review-if-changed" % (
        source["name"],
        latest,
    )


def main(argv):
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    config = root / "skills" / "redmuse-update" / "sources.yaml"
    if not config.exists():
        print("sources.yaml not found at %s" % config, file=sys.stderr)
        return 2
    try:
        sources = parse_sources(config)
    except ValueError as error:
        print("bad sources.yaml: %s" % error, file=sys.stderr)
        return 2
    for source in sources:
        kind = source["kind"]
        if kind == "self":
            print(check_self(root, source))
        elif kind == "reference":
            print(check_reference(source))
        elif kind == "manual":
            print("%s | n/a | none | manual" % source["name"])
        else:
            print("unknown kind %r for source %s" % (kind, source["name"]), file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
