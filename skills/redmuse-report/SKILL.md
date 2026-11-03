# RedMuse reporting

You turn redmuse findings into a ranked report and a retest loop.
Your job is honesty: severity by reachability and impact, dedupe by
root cause, and a coverage statement that says exactly what was and was
not probed.

## Severity

Order findings critical, high, medium, low, info. Assign severity by
these two questions, in this order:

- Reachability: can an attacker actually trigger it, with what access?
  Unauthenticated and trivial beats authenticated and complex.
- Impact: what does it actually gain? Data, access, execution, or
  money movement beats theoretical exposure.

A theoretical issue with no reachable path is info or low, never
critical. A confirmed issue with a trivial proof and real impact is
critical or high. When in doubt, downgrade and say why.

## Dedupe

Merge findings that share a root cause into one finding with all
affected endpoints listed. Do not inflate the count with the same bug on
ten endpoints. Keep a separate count of affected endpoints inside the
merged finding.

## Report files

Write all of these under redmuse-runs/<run-name>/:

- report.md: executive summary, scope and coverage statement, ranked
  findings with impact and fix per finding, unvalidated section, and
  probed-but-clean classes.
- findings.json: machine-readable findings following templates/report.md
  shape: id, title, severity, status, endpoint, method, parameter,
  CWE when known, proof summary, fix.
- vulnerabilities/<finding-id>.md: one file per confirmed finding with
  full proof (request and response), impact, and fix.
- run-log.md: updated with the final outcome, budgets used, and any
  partial coverage notes.

## Coverage statement

Every report states: target, scope, mode, budgets used, phases run,
classes probed, classes not probed and why, and whether the run was
complete or partial. A partial run is never called clean. A clean report
means no finding in the probed surface, and says exactly that.

## Retest

After fixes, re-run only the proofs for fixed findings. Record per
finding: fixed, still open, or changed. Update the finding status, never
rewrite history. A retest that cannot reproduce the original proof
because the feature changed is marked changed, with a note.
