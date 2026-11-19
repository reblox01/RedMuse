#!/usr/bin/env python3
"""RedMuse findings store. Standard library only, no dependencies.

A SQLite store for findings across runs, so a finding survives
the session that found it, can be queried by severity, CWE, and
status, and can be handed off between runs. One database per
run folder, or one shared database per target, your choice.
Never store secrets, tokens, session cookies, or other users'
real data in it. A finding record holds the proof capsule
reference, not the credential.

History is append-only. Re-adding a finding id never destroys
the earlier record: the new revision is appended to
findings_history, and the findings table keeps the latest
revision only, with the original created_at preserved. The
history rows keep the original proof, every previous status,
and the run identifier from REDMUSE_RUN_ID when set.

Export writes the object shape tools/render_report.py reads:
findings, counts, target, mode, outcome, and run. The outcome
defaults to partial, because the store alone cannot prove a
complete run; pass --outcome complete only when the run that
filled the store actually completed its coverage.

Usage:
  python3 tools/findings.py init --db redmuse-runs/demo/findings.db
  python3 tools/findings.py add --db <db> --id idor-user-profile \
      --title "IDOR on /user" --severity high --cwe CWE-639 \
      --endpoint "/user?id=2" --status verified --confidence 5
  python3 tools/findings.py list --db <db> --status verified
  python3 tools/findings.py stats --db <db>
  python3 tools/findings.py export --db <db> --out findings.json
  python3 tools/findings.py handoff --db <db> --out handoff.md
"""
import argparse
import json
import os
import sqlite3
import sys

SCHEMA = """
CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    cwe TEXT,
    endpoint TEXT,
    status TEXT NOT NULL DEFAULT 'candidate',
    confidence INTEGER NOT NULL DEFAULT 0,
    proof TEXT,
    ratings_by_reviewer TEXT DEFAULT '',
    shared_rating TEXT DEFAULT '',
    run_id TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS findings_history (
    revision INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    cwe TEXT,
    endpoint TEXT,
    status TEXT NOT NULL,
    confidence INTEGER NOT NULL DEFAULT 0,
    proof TEXT,
    ratings_by_reviewer TEXT DEFAULT '',
    shared_rating TEXT DEFAULT '',
    run_id TEXT DEFAULT '',
    recorded_at TEXT DEFAULT (datetime('now'))
);
"""

# Columns added after the first schema version. Databases created
# before them gain the columns on first connect, so an old store
# keeps working and keeps its history.
EXTRA_COLUMNS = ("ratings_by_reviewer", "shared_rating", "run_id")

SEVERITIES = {"critical", "high", "medium", "low", "info"}
STATUSES = {"verified", "candidate", "rejected", "blocked", "fixed", "still-open"}


def connect(db):
    conn = sqlite3.connect(db)
    conn.executescript(SCHEMA)
    existing = {row[1] for row in conn.execute("PRAGMA table_info(findings)")}
    for col in EXTRA_COLUMNS:
        if col not in existing:
            conn.execute(f"ALTER TABLE findings ADD COLUMN {col} TEXT DEFAULT ''")
    conn.commit()
    return conn


def cmd_init(args):
    connect(args.db)
    print(f"initialised {args.db}")


def cmd_add(args):
    if args.severity not in SEVERITIES:
        print(f"bad severity: {args.severity}", file=sys.stderr)
        return 2
    if args.status not in STATUSES:
        print(f"bad status: {args.status}", file=sys.stderr)
        return 2
    if not 0 <= args.confidence <= 5:
        print("confidence must be 0-5", file=sys.stderr)
        return 2
    run_id = os.environ.get("REDMUSE_RUN_ID", "")
    conn = connect(args.db)
    cur = conn.execute(
        "INSERT INTO findings_history "
        "(id, title, severity, cwe, endpoint, status, confidence, proof, "
        "ratings_by_reviewer, shared_rating, run_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (args.id, args.title, args.severity, args.cwe, args.endpoint,
         args.status, args.confidence, args.proof,
         args.ratings_by_reviewer, args.shared_rating, run_id),
    )
    revision = cur.lastrowid
    conn.execute(
        "INSERT INTO findings "
        "(id, title, severity, cwe, endpoint, status, confidence, proof, "
        "ratings_by_reviewer, shared_rating, run_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(id) DO UPDATE SET "
        "title = excluded.title, severity = excluded.severity, "
        "cwe = excluded.cwe, endpoint = excluded.endpoint, "
        "status = excluded.status, confidence = excluded.confidence, "
        "proof = excluded.proof, "
        "ratings_by_reviewer = excluded.ratings_by_reviewer, "
        "shared_rating = excluded.shared_rating, "
        "run_id = excluded.run_id",
        (args.id, args.title, args.severity, args.cwe, args.endpoint,
         args.status, args.confidence, args.proof,
         args.ratings_by_reviewer, args.shared_rating, run_id),
    )
    conn.commit()
    print(f"stored {args.id} (revision {revision}, {args.status}, "
          f"confidence {args.confidence})")
    return 0


def cmd_list(args):
    conn = connect(args.db)
    query = "SELECT id, title, severity, status, confidence FROM findings"
    params = []
    if args.status:
        query += " WHERE status = ?"
        params.append(args.status)
    if args.severity:
        query += " AND" if args.status else " WHERE"
        query += " severity = ?"
        params.append(args.severity)
    query += " ORDER BY severity, id"
    for row in conn.execute(query, params):
        print(" | ".join(str(v) for v in row))
    return 0


def cmd_stats(args):
    conn = connect(args.db)
    total = conn.execute("SELECT COUNT(*) FROM findings").fetchone()[0]
    revisions = conn.execute("SELECT COUNT(*) FROM findings_history").fetchone()[0]
    print(f"total: {total}")
    print(f"revisions: {revisions}")
    for label, col in (("by severity", "severity"), ("by status", "status")):
        print(f"{label}:")
        for value, count in conn.execute(
            f"SELECT {col}, COUNT(*) FROM findings GROUP BY {col} ORDER BY COUNT(*) DESC"
        ):
            print(f"  {value}: {count}")
    return 0


def cmd_export(args):
    conn = connect(args.db)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM findings ORDER BY id")]
    counts = {sev: 0 for sev in sorted(SEVERITIES)}
    for row in rows:
        counts[row["severity"]] = counts.get(row["severity"], 0) + 1
    data = {
        "findings": rows,
        "counts": counts,
        "target": args.target,
        "mode": args.mode,
        "outcome": args.outcome,
        "run": os.environ.get("REDMUSE_RUN_ID", ""),
    }
    with open(args.out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"exported {len(rows)} findings to {args.out}")
    return 0


def cmd_handoff(args):
    conn = connect(args.db)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM findings WHERE status NOT IN ('rejected', 'fixed') ORDER BY severity, id")]
    lines = ["# Findings handoff", "", f"Open findings: {len(rows)}", ""]
    for r in rows:
        lines.append(f"- {r['id']} [{r['severity']}] ({r['status']}, confidence {r['confidence']}): {r['title']}")
    with open(args.out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {args.out} with {len(rows)} open findings")
    return 0


def main():
    parser = argparse.ArgumentParser(description="RedMuse findings store")
    parser.add_argument("--db", required=True, help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    add = sub.add_parser("add")
    add.add_argument("--id", required=True)
    add.add_argument("--title", required=True)
    add.add_argument("--severity", required=True)
    add.add_argument("--cwe", default="")
    add.add_argument("--endpoint", default="")
    add.add_argument("--status", default="candidate")
    add.add_argument("--confidence", type=int, default=0)
    add.add_argument("--proof", default="")
    add.add_argument("--ratings-by-reviewer", default="")
    add.add_argument("--shared-rating", default="")
    lst = sub.add_parser("list")
    lst.add_argument("--status")
    lst.add_argument("--severity")
    sub.add_parser("stats")
    exp = sub.add_parser("export")
    exp.add_argument("--out", required=True)
    exp.add_argument("--target", default="")
    exp.add_argument("--mode", default="")
    exp.add_argument("--outcome", default="partial",
                     help="complete, partial, or clean; defaults to partial")
    hand = sub.add_parser("handoff")
    hand.add_argument("--out", required=True)
    args = parser.parse_args()
    commands = {"init": cmd_init, "add": cmd_add, "list": cmd_list,
                "stats": cmd_stats, "export": cmd_export, "handoff": cmd_handoff}
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
