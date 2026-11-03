# Report

## Executive summary

A redmuse quick run against the localhost test target confirmed four
real flaws plus one info note. An unauthenticated visitor can read any
user's profile, including an admin account, through both the web page
and the API. Search reflects input unescaped, enabling reflected XSS.
The redirect endpoint sends visitors to any URL. No security headers
are set. All proofs were reproduced live on localhost.

## Scope and coverage

- Target: http://127.0.0.1:8901 (redmuse test target, localhost only)
- Scope in: /, /user, /search, /redirect, /api/users
- Scope out: everything else on the machine, all remote hosts
- Mode: quick
- Budgets used: 6 active probes, under 5 minutes, 1 team
- Phases run: recon, web exploitation, API exploitation
- Classes probed: IDOR, BOLA, reflected XSS, open redirect, security
  headers
- Classes not probed, and why: SQL injection (no database), auth flaws
  (no real auth), SSRF (no URL fetch feature), stored XSS (no stored
  content)
- Run outcome: complete

## Findings

### High: IDOR on /user?id=

- Endpoint: GET /user?id=2
- Parameter: id
- CWE: 639
- Proof: requesting id=2 as an unauthenticated visitor returned the
  admin profile (Bob Test, role admin, balance 99999), while id=1
  returned a regular user. No ownership check exists.
- Impact: any visitor reads any user's data, including admin accounts.
- Fix: check that the caller owns the requested profile, or holds an
  admin role, before returning it. Deny by default.

### High: API BOLA on /api/users/<id>

- Endpoint: GET /api/users/2
- Parameter: path id
- CWE: 639
- Proof: requesting /api/users/2 with no token returned the admin user
  object as JSON, including email, role, and balance.
- Impact: same as the web IDOR, through the API, in machine-readable
  form.
- Fix: require authentication on the API and enforce the same
  ownership check as the web route. Both are one root cause with the
  web IDOR, fixed together.

### Medium: reflected XSS on /search?q=

- Endpoint: GET /search?q=
- Parameter: q
- CWE: 79
- Proof: the marker musestrix-probe-123 was reflected, and the payload
  <script>alert(1)</script> was reflected unescaped in the response.
- Impact: an attacker link can run script in a victim's browser in the
  site's context.
- Fix: escape all reflected input on output, and prefer a templating
  engine that escapes by default.

### Low: open redirect on /redirect?url=

- Endpoint: GET /redirect?url=
- Parameter: url
- CWE: 601
- Proof: requesting url=https://example.com returned 302 to
  https://example.com, with any URL accepted.
- Impact: phishing links that look like they come from this site.
- Fix: allow only relative paths or an allowlist of hosts, and reject
  everything else.

### Info: missing security headers

- Endpoint: every response
- Proof: responses carry only Server, Date, Content-Type, and
  Content-Length. No Content-Security-Policy, frame protection,
  nosniff, or Referrer-Policy is set.
- Fix: add the four headers in the server config. Info level on its
  own, defense in depth once the real flaws are fixed.

## Unvalidated

None. Every candidate reproduced.

## Probed but clean

SQL injection, auth flaws, SSRF, and stored XSS were out of scope for
this target (no database, no real auth, no URL fetch, no stored
content), so they were not probed rather than probed clean.

## Retest

Not run yet. Re-run only the four proofs after fixes.
