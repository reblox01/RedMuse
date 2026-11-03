# Finding record

One file per confirmed finding, under
`muse-strix-runs/<run-name>/vulnerabilities/<finding-id>.md`.

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
