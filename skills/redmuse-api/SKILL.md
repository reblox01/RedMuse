# RedMuse API exploitation

You test an API black-box for a redmuse run, following the OWASP API
Security Top 10. Enumerate first, exploit second. Every finding ships
with a reproduced proof of concept request, or it is not a finding.

## Enumeration

- Build the endpoint inventory from the recon output, OpenAPI or GraphQL
  schema when available, and JS bundle analysis. Include undocumented
  endpoints and old versions (v1 beside v2 is a classic).
- Map auth per endpoint: which need a token, which accept none, and
  which accept a token of the wrong type or scope.
- Map object references: every id in paths, bodies, and GraphQL
  arguments, plus list and search endpoints that leak ids.

## Classes, in priority order

- Broken object level authorization (BOLA and IDOR): request another
  user's object with your own token. Try horizontal, vertical, and
  cross-tenant access. Try type changes, edge values, and duplicate
  keys.
- Broken authentication: tokens that never expire, weak signing, auth
  endpoints without rate limits on test accounts, password reset flaws.
- Broken object property level authorization: excessive data exposure
  (fields returned that the client never shows) and mass assignment
  (fields accepted that the client never sends, like role or balance).
- Broken function level authorization: call admin or staff functions
  with a low-privilege token.
- Unrestricted resource consumption: pagination without caps, bulk
  endpoints, expensive queries. Prove with a small request, never with
  a real flood.
- SSRF: URL fields and webhook targets pointed at internal endpoints
  with a harmless canary. Stop at proof of reachability.
- Injection: SQL, NoSQL, and command injection with benign markers.
  Never with destructive statements.
- Security misconfiguration and inventory failures: verbose errors,
  debug endpoints, shadow APIs, and missing security headers.

## Payload discipline

- One variable at a time, harmless markers only, test accounts only.
- Log every attempt: full request, full response, and result. The
  orchestrator reproduces from your log.

## Probe shapes

- Silent non-standard statuses. Grep repo-wide for non-standard
  status returns (499, 444, 440) and confirm each one has a log line
  or is intentionally silent. Example probe: `grep -rn "499\|444\|440"`
  plus a check of nearby logging (`console`, logger calls) for each
  hit. A status that returns silently, with no log line, is a
  finding; an intentionally silent one must be recorded as such, not
  left unexamined.
- Busy-database 503 is a timeout to a short-timeout client. When an
  API returns 503 after a long database busy wait (for example a 5s
  `busy_timeout` producing a hang of about 5.042s before the 503),
  record that a client with a shorter timeout sees this as a
  timeout, not a 503. Do not report the 503 alone as the client
  experience. The retry guidance for this path belongs in the API
  docs: state the expected wait, the retryable status, and a
  backoff, so a caller can distinguish a busy-database retry from a
  real failure.

## Output

Return one finding record per confirmed class, in the orchestrator shape:
id, title, severity guess, endpoint, method, parameter, proof (exact
request and response), impact, and root cause fix. List probed-but-clean
classes separately with what was tried.
