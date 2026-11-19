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

## The well-formed finding (NEW-B3 template)

Every finding in the report follows this template. Most fields
in it are conditional on finding type, and workers apply only
the fields that match their finding. The template is not one
checklist every finding must fill in full: a field whose type
label does not match the finding stays blank, it is not
invented. The NEW-B3 shape below started from one scanner
finding (exact function, exact missing words, a concrete
shape, plus near-miss cases), and that precision is why its
fix was verifiable in one suite run. The same conditional
discipline applies to every other type: an IDOR, an SSRF, or
an auth bypass applies the mechanism, citation, and rating
fields, and leaves the scanner-only fields (real shape,
siblings) blank. A finding that does not meet the template
stays unvalidated until the missing piece is supplied;
redmuse-verify sends it back under its finding-quality checks.

Required fields, in addition to id, title, severity, endpoint,
method, parameter, CWE, proof, and fix:

- mechanism: the mechanism that fails, not only the symptom.
  Name the check or function and the exact behaviour
  (example: the 2-row jump inside a column run that
  columnRowsMonotonic rejects).
- discriminator (false positives only): the rule that
  separates the must-pass case from the must-stay-rejected
  cases. State both sets next to each other, or state the
  intended rule in one line (example: coverage, not
  adjacency).
- citation: identifier exactly as written in code, plus file
  path, line number, and the literal string where one
  matters (example: route.ts:42 / :45 and the exact 409
  strings). Never a reconstructed ID.
- real shape (scanner findings): one example query per
  keyword, naming the real SQL shape, not just the keyword.
  Examples: ORDER BY ? NULLS FIRST, ORDER BY ? COLLATE "C",
  FETCH FIRST ? ROWS ONLY.
- siblings (fixed allow/blocklist findings): every sibling
  keyword in the same clause family, enumerated and either
  covered or explicitly scoped out with a reason. Examples
  next to ROWS: RANGE / GROUPS, ROW; next to FIRST: NEXT;
  plus ESCAPE / TO and INTERVAL units. A list finding that
  does not ask "what are the siblings of this list?" is
  incomplete.
- consumers (shared-helper findings): a full consumer table,
  every consumer of the shared helper's return value, not
  just the files the reporter happened to open. Each row:
  consumer, file and line, how it uses the return value,
  and what happens on each branch.
- caller recovery (false-failure findings): the caller's
  next step and whether recovery is possible, not just that
  the status code is wrong. Example: a rotate false 409
  means the new key was issued but never delivered, the old
  key is dead, and retry is impossible, so the outcome is
  key loss.
- check-whether phrasing (list findings): when a finding
  adds X to a list, phrase it as a check, not an assertion
  of state: "check whether X is already in list A and
  missing from list B", then record what was actually
  found. Example: FIRST turned out to be in neither list;
  asserting it was in one would have been a wrong
  assumption baked into the finding.
- ratings by reviewer (multi-reviewer findings): each
  reviewer's severity rating with the reason, recorded when
  two reviewers rate the same shape differently.
- shared rating (multi-reviewer findings): the one shared
  rating the reviewers agreed, with the reason; or the
  split, with each rating and reason shown plainly in the
  report. A severity reconciled by the coordinator alone,
  with no reviewer reason on file, is not a calibrated
  rating.

Worked shape, NEW-B3 style: function startsValue, missing
words FIRST and NEXT, concrete shape FETCH FIRST ? ROWS ONLY,
near-miss cases listed, siblings ROW / RANGE / GROUPS
enumerated, and one real shape per keyword. Copy that shape;
do not copy its words.

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
When a finding claims a log branch, the coverage statement lists
which branches were actually exercised and which were unreachable
via the probed route (example: the 0 / -1 branches unreachable
via HTTP); only the exercised branches count as proven.

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
