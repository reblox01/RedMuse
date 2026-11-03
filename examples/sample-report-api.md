# Report

## Executive summary

A muse-strix API run against the localhost API test target confirmed
four flaws, all in the OWASP API Security Top 10. An unauthenticated
caller reads any user, reads internal fields in list responses, creates
an admin account through mass assignment, and opens the admin stats
endpoint with no auth check. All proofs were reproduced live on
localhost.

## Scope and coverage

- Target: http://127.0.0.1:8902 (muse-strix API test target)
- Scope in: /api/v1/users, /api/v1/users/<id>, /api/v1/admin/stats
- Scope out: everything else on the machine, all remote hosts
- Mode: quick
- Budgets used: 4 active probes, under 5 minutes, 1 team
- Phases run: recon, API exploitation
- Classes probed: BOLA, excessive data exposure, mass assignment,
  broken function level authorization
- Classes not probed, and why: broken authentication (no real auth),
  injection (no query layer), SSRF (no URL fields), rate limits (not
  an API flaw class for this target)
- Run outcome: complete

## Findings

### High: BOLA on GET /api/v1/users/<id>

- Endpoint: GET /api/v1/users/2
- Parameter: path id
- CWE: 639
- Proof: no token, full admin user object returned, including email,
  role, salary band, and internal note.
- Fix: require authentication and enforce ownership or admin role per
  object.

### High: mass assignment on POST /api/v1/users

- Endpoint: POST /api/v1/users
- Parameter: body field role
- CWE: 915
- Proof: posting name, email, and role admin created user id 3 with
  role admin, no privilege check.
- Fix: allowlist writable fields at the API layer. Never bind role,
  balance, or permission fields from client input.

### Medium: broken function level authorization on /api/v1/admin/stats

- Endpoint: GET /api/v1/admin/stats
- Parameter: none
- CWE: 862
- Proof: no token, admin stats returned, including revenue estimate.
- Fix: require an admin role on every admin endpoint, checked server
  side.

### Medium: excessive data exposure on GET /api/v1/users

- Endpoint: GET /api/v1/users
- Parameter: none
- CWE: 200
- Proof: list responses include salary_band and internal_note for
  every user, fields the client never shows.
- Fix: return only the fields the client needs, through a response
  serializer per endpoint.

## Unvalidated

None. Every candidate reproduced.

## Retest

Not run yet. Re-run only the four proofs after fixes.
