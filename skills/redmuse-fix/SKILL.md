# RedMuse fix and retest

You fix redmuse findings at the root cause and prove each fix with
a retest. You triage by severity, patch the cause, and re-run only the
affected proofs. You never close a finding without a retest.

## Triage

Order the work critical, high, medium, low, info, and within a severity
by reachability: unauthenticated and trivial first. Merge findings
that share a root cause into one fix. A fix that covers ten endpoints
is one fix, not ten.

## Patch rules

- Fix the cause, not the symptom. An ownership check belongs in the
  authorization layer, not in one route. Output encoding belongs in
  the template layer, not in one handler.
- Prefer framework features over hand-rolled checks: parameterized
  queries, escaping templating, auth libraries, and allowlists.
- Keep the patch minimal and reviewable. A fix that rewrites a module
  is a refactor, not a patch, and needs its own review.
- Never paste a found secret into code, tests, or reports. Rotate a
  leaked secret at its source, then remove it from the codebase and
  its history handling per the owner's policy.

## Retest

For each fixed finding, re-run only its original proof, unchanged:

- Proof no longer reproduces: mark fixed, with the retest request and
  response attached.
- Proof still reproduces: mark still open, and say what the patch
  missed.
- Feature changed so the proof no longer applies: mark changed, with a
  note on what replaced it.

Update finding statuses in findings.json and the per-finding files.
Never rewrite the original proof or history. A retest that cannot run
(for example the target is down) is marked blocked, not fixed.

## Output

Return a fix report: per finding, the patch summary (files changed,
lines, approach), the retest result, and the new status. List fixes
that need a decision from the owner (migration, breaking change,
secret rotation) separately from fixes already applied.
