# Finding record

One file per confirmed finding, under
`redmuse-runs/<run-name>/vulnerabilities/<finding-id>.md`.

- id: short slug.
- title: one line.
- severity: critical, high, medium, low, or info.
- status: open, fixed, still open, changed, or unvalidated.
- endpoint: method and path.
- parameter: the parameter or field exploited.
- CWE: CWE number when known, else blank.
- proof: the exact request and the exact response that reproduce it,
  with a harmless marker. No destructive payloads.
- expected behavior: what a secure target would return for the
  exact request in proof.
- observed behavior: what the target actually returned.
- authorization context: the account, role, token scope, or
  unauthenticated state the proof ran under, plus the scope
  that authorized it.
- verification status: unvalidated, verified, candidate,
  rejected, or blocked, with the proof capsule reference.
- NEW-B3 fields (conditional by finding type, see redmuse-report):
  mechanism, discriminator, citation, real shape, siblings,
  consumers, caller recovery. Apply only the fields that match
  the finding type; the rest stay blank.
- ratings by reviewer: each reviewer's severity rating with the
  reason, recorded when two reviewers rate the same shape
  differently.
- shared rating: the one shared rating the reviewers agreed,
  with the reason; or the split, with each rating and reason
  shown plainly.
- impact: what an attacker actually gains.
- fix: the root cause fix.
- affected endpoints: other endpoints with the same root cause, if any.
- confirmed_by: skills that independently confirmed this finding.
- confidence: score 0 to 5 and band (corroborated, confirmed, weak,
  unvalidated), with the points breakdown.
- cve: vulnerability id when the finding came from a CVE intel
  record, else blank.
- fixed version: the patched version from the CVE record, else blank.
- cve status: applicable, not-applicable, unvalidated, or
  check-incomplete, when a CVE record exists.
- exploit selected: the safe check run for the CVE record, else blank.
