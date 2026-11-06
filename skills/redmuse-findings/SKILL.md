# RedMuse findings store

You keep findings across runs, so a finding survives the
session that found it. A run log is a story, a findings store
is a memory: it can be queried by severity, CWE, and status,
it can be exported, and it can be handed off to the next run.
Every finding that reaches the report goes in the store, and
every finding in the store has a status that says where it
stands right now.

## The tool

tools/findings.py, Python standard library only, SQLite, no
dependencies. One database per run folder, or one shared
database per target, the run log says which. Commands: init,
add, list, stats, export, handoff. See the tool's own help
text for the exact arguments.

## Rules

- One record per finding, keyed by id. Adding the same id
  again replaces it, it does not duplicate it. A finding
  that was re-verified updates its status and confidence,
  it does not become a second finding.
- Status values, only these: verified, candidate, rejected,
  blocked, fixed, still-open. A finding that was never
  verified is candidate, never verified. A finding that was
  fixed is fixed only after redmuse-fix retested it, never
  because someone said it was fixed.
- Confidence 0 to 5, same scale as the ensemble. A verified
  finding needs 4 or 5.
- Never store secrets, tokens, session cookies, or other
  users' real data. A record holds the proof capsule
  reference, a replay command, and a redacted excerpt, not
  the credential.
- The handoff command writes the open findings for the next
  run: verified and candidate and blocked, never rejected
  and never fixed. A handoff is how a run continues, not
  how it forgets.

## Output

After every phase that produces findings, add or update the
records, then run stats and put the totals in run-log.md:
total, by severity, by status. A run that skipped the store
says so in its report, and its findings live only in the
report file, with no queryable record.
