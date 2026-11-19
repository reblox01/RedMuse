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
- CSRF: missing or bypassable token on state-changing API requests.
  Submit a state-changing call (POST, PUT, PATCH, DELETE) once with
  the token or session cookie the client normally sends, once with no
  token, once with a wrong or empty token, and once with a token from
  another session. After each call, read back the affected object to
  check whether the state actually changed. Proof is a state change
  without a valid token, or with another session's token. A 401, 403
  or 400 that blocks the no-token call is clean, not a finding.
- CORS misconfiguration: a permissive Access-Control-Allow-Origin
  header on API responses that carry credentials or sensitive data.
  Send a request with `Origin: https://evil.example` and record the
  Access-Control-Allow-Origin and Access-Control-Allow-Credentials
  headers; repeat with an OPTIONS preflight carrying
  Access-Control-Request-Method and Access-Control-Request-Headers.
  Proof is an ACAO that reflects an arbitrary Origin combined with
  `Access-Control-Allow-Credentials: true`, or a wildcard ACAO with
  credentials true. A wildcard ACAO with no credentials on a public,
  non-sensitive endpoint is low or info, not a confirmed finding.
  A response with no ACAO header at all is clean for this class.
- Injection: SQL, NoSQL, and command injection with benign markers.
  Never with destructive statements.
- Security misconfiguration and inventory failures: verbose errors,
  debug endpoints, shadow APIs, and missing security headers.

## Payload discipline

- One variable at a time, harmless markers only, test accounts only.
- Log every attempt: full request, full response, and result. The
  orchestrator reproduces from your log.

## GraphQL

If the target exposes a GraphQL endpoint (usually /graphql), test
these classes. Each class needs probe steps, expected vs observed
behavior, and evidence. A GraphQL endpoint with no dedicated probes
is untested, not clean.

- Introspection abuse. Probe: POST `{"query": "{ __schema { types
  { name } } }"}` to the endpoint, then request field lists for the
  types returned. Expected: introspection disabled in production, or
  the schema restricted to what the client needs. Observed: record
  the exact response. Proof is a returned schema that exposes types,
  fields, or mutations the client never uses. An introspection query
  that returns an error is clean for this class.
- Query depth and complexity resource consumption. Probe: send a
  shallow query first and record response time and size, then the
  same shape nested one level deeper at a time (for example user,
  then user friends, then friends of friends), still with small
  result sets. Expected: the server rejects or caps queries past a
  stated depth or complexity limit. Observed: record time, size, and
  status per depth. Proof is response time or size growing sharply
  with depth and no cap firing. Never send a real flood; a small
  depth ladder proves the missing cap.
- Batching attacks. Probe: send one request carrying an array of
  several queries (for example several login or password-reset
  mutations in a single batch) and count how many executed. Expected:
  batching disabled, or a small batch limit, or per-query rate
  limits that still apply inside a batch. Observed: record how many
  of the batched operations ran and their results. Proof is a batch
  that executes operations past the single-request rate limit, for
  example many login attempts in one HTTP request with no 429.
- Authorization bypass via field aliases. Probe: with a low-privilege
  token, request the same field twice under different aliases with
  different arguments in one query, for example `a: user(id: "1")
  { name }` and `b: user(id: "2") { name }`, where id 2 belongs to
  another user. Expected: the authorization check applies per field
  resolution, so the other user's object is denied. Observed: record
  which alias returned data and which was denied. Proof is the
  other user's data returned under the aliased field while the
  direct request for the same object is denied or would be denied.
- Evidence for every GraphQL finding: the exact query sent, the full
  response, the token privilege used, and the expected vs observed
  behavior above. A query that returns data is not proof on its own;
  the comparison against the expected behavior is what makes it a
  finding.

## gRPC

gRPC methodology in this skill is thin: there is no probe section for
it yet, and this paragraph does not invent one. A full gRPC section
must cover, at minimum: service enumeration (which services and
methods are exposed, including server reflection when enabled),
method authorization (each method called with a low-privilege
credential, not just the ones the client calls), and message
validation (malformed, oversized, or unexpected fields and how the
server handles them). Until that section exists, record any gRPC
endpoint found as untested coverage, not as clean.

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
