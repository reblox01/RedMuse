# Ensemble sample report

Worked example. The localhost findings below are real, proven in
the dev-audit demo (live proof plus traced code path). The
external-skill columns are shown for shape and marked not-run
here, since those skills are not installed on the demo machine.
Nothing below claims an external skill ran.

## Merged findings

### IDOR on /user, high, score 3, confirmed

- Candidates merged: redmuse-web live probe (GET /user?id=2
  returned the admin profile with no auth) and redmuse-code trace
  (test-target/app.py /user branch, no ownership check).
- confirmed_by: redmuse-web, redmuse-code.
- Points: live proof 2, code path 1, extra skills 0. Total 3.
- Band: confirmed. With OWASP and Sentry installed, two extra
  confirming skills would add 2 points, total 5, corroborated.
  That upgrade is shown, not claimed.

### Reflected XSS on /search, medium, score 3, confirmed

- Candidates merged: redmuse-web live probe (marker reflected
  unescaped) and redmuse-code trace (/search branch, query
  reflected without escaping).
- confirmed_by: redmuse-web, redmuse-code.
- Points: live proof 2, code path 1, extra skills 0. Total 3.
- Band: confirmed.

### Open redirect on /redirect, low, score 3, confirmed

- Candidates merged: redmuse-web live probe (302 to an outside
  URL) and redmuse-code trace (/redirect branch, any url accepted).
- confirmed_by: redmuse-web, redmuse-code.
- Points: live proof 2, code path 1, extra skills 0. Total 3.
- Band: confirmed.

## Why merging matters here

A live-only run sees the symptom: admin data comes back for
id=2. A code-only run sees the cause: no ownership check in the
handler. Either alone is a finding; merged, the finding carries
both the proof and the root cause, and the fix targets the check
instead of the endpoint. That is the ensemble effect: one view
misses what the other catches, and the merged record is stronger
than either candidate.

## Coverage matrix, excerpt

Rows are classes, columns are assigned skills. Found means the
skill found something in that class, clean means probed with
nothing found, skipped means not installed here, gap means no
skill was assigned at all.

- IDOR: redmuse-web found, redmuse-code found, OWASP skipped,
  Sentry skipped. Merged into one finding, not counted twice.
- XSS: redmuse-web found, redmuse-code found, OWASP skipped,
  Sentry skipped. Merged into one finding.
- Open redirect: redmuse-web found, redmuse-code found.
  Merged into one finding.
- Session handling: redmuse-web probed lightly, single coverage,
  flagged. No auth skill ran in this demo.
- Missing security headers: redmuse-web probed, single coverage,
  info level.
- SSRF: gap. No skill was assigned to this class in the quick
  localhost run. Listed as a gap, never as clean.

## Disagreements

None in this example. The rule stands: when skills disagree, the
proof decides. A reproduced proof beats a clean opinion, and a
disagreement with no proof stays unvalidated with the
disagreement noted.
