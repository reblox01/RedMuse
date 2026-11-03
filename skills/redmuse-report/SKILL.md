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
  probed-but-clean classes, plus a CVE intel section: shortlist
  table, what was checked, what was skipped and why, and source
  status.
- findings.json: machine-readable findings following templates/report.md
  shape: id, title, severity, status, endpoint, method, parameter,
  CWE when known, proof summary, fix, plus cve id, fixed version,
  cve status, and exploit selected when the finding came from a
  CVE intel record.
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

## Ensemble scoring

Assign overlapping skills to the same surface on purpose, so one
skill missing something does not end the story. Overlap pairs:

- Code: redmuse-code, OWASP owasp-security, Sentry security-review,
  Cloudflare security-audit.
- Web: redmuse-web, Masriyan 09-web-security.
- API: redmuse-api, Masriyan 09-web-security.
- Auth: redmuse-auth, OWASP owasp-security, Masriyan 09-web-security.
- CI and diff: redmuse-ci, Sentry gha-security-review, Trail of Bits
  differential-review, OpenAI security-diff-scan.
- Recon: redmuse-recon, Masriyan 01-recon-osint.
- Dependencies and static analysis: Masriyan 02-vulnerability-scanner,
  Trail of Bits semgrep and codeql, sarif-parsing for their output.
- AI and agent: Securly, Masriyan 16-ai-llm-security, OWASP LLM and
  Agentic Top 10.
- Network: Masriyan 08-network-security alone, so flag it as single
  coverage whenever it is the only skill on that surface.

Merge findings that share endpoint, parameter, and CWE, or that
share a root cause and data flow, into one finding. The merged
finding lists every confirming skill in confirmed_by, keeps the
strongest proof, and keeps the affected endpoints count from
dedupe.

Score confidence from evidence, not from how many tools ran:

- Live proof of concept reproduced: 2 points.
- Code path traced to the flaw: 1 point.
- Each additional independent skill confirming, beyond the first:
  1 point, capped at 2.
- Total 0 to 5. Bands: 4 to 5 corroborated, 2 to 3 confirmed,
  1 weak, 0 unvalidated.
- A live proof alone is still confirmed, as before. Ensemble only
  adds corroboration on top, it never lowers a reproduced proof.
- A code-only pattern with no live proof is weak, never confirmed.
  It goes in the report as weak with its follow-up step, not in
  the confirmed list.
- When skills disagree, the proof decides. A reproduced proof beats
  a clean opinion, and a disagreement with no proof stays
  unvalidated with the disagreement noted.

Coverage matrix: the report lists every class against the skills
assigned to it, marked probed, found, clean, or not probed. A class
with no assigned skill is a gap, listed as a gap, never as clean.
A class probed by exactly one skill is flagged single coverage.
That matrix is how a reader sees what one skill missed and another
caught, and what nobody probed at all.
