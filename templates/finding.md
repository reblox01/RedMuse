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
