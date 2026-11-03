# Dev-audit sample report

## Scope and gate

- Target: http://127.0.0.1:8901 (RedMuse web test target, localhost only)
- Code: test-target/app.py, fake data only
- Scope in: /, /user, /search, /redirect
- Scope out: everything else on the machine, all remote hosts
- Mode: dev-audit, quick budgets
- Authorization: owner demo run on localhost, recorded here
- Run outcome: complete for the probed classes

## Phase 1: code audit

### High: IDOR on /user

- Code location: test-target/app.py, do_GET, /user branch, line 60,
  planted flaw comment line 66: no ownership check, any id returns
  that user.
- Flow: query parameter id goes straight to a USERS lookup and the
  result is returned, with no session or ownership check anywhere in
  the handler.
- Fix: check that the caller owns the requested profile, or holds an
  admin role, before returning it. Deny by default.

### Medium: reflected XSS on /search

- Code location: test-target/app.py, /search branch, line 73,
  planted flaw comment line 75: query reflected without escaping.
- Flow: query parameter q is interpolated directly into the HTML
  response.
- Fix: escape all reflected input on output, and prefer a templating
  engine that escapes by default.

### Low: open redirect on /redirect

- Code location: test-target/app.py, /redirect branch, line 77,
  planted flaw comment line 79: open redirect, any url accepted.
- Flow: query parameter url is passed straight to the Location
  header of a 302 response.
- Fix: allow only relative paths or an allowlisted host set, and
  reject everything else.

## Phase 2: live proofs

All three code findings reproduced live on localhost:

- IDOR: GET /user?id=2 with no auth returned the admin profile
  (role admin, balance 99999), while id=1 returned a regular user.
- XSS: GET /search?q=musestrix-probe-123 returned the marker in the
  response, unescaped.
- Redirect: GET /redirect?url=https://example.com returned 302 to
  https://example.com.

## Phase 3: Cloudflare edge checklist

Not probed. Localhost has no edge, no WAF, and no Cloudflare
dashboard in scope. Recorded as not probed, never as clean. The
responses carry no security headers (Server, Date, Content-Type,
and Content-Length only), noted as info level.

## Securly layers

Skipped with reason. The target is a plain web app with no AI
chatbot, LLM, agent, or mobile surface, so the agent, LLM, and
mobile layers do not apply. The OWASP baseline is covered by the web
skill findings above.

## Phase 4: exploit scenario, unauthenticated chain

A visitor with no account reads any user's data, including an admin
account, through /user?id=2; crafts a search link that reflects
script in a victim's browser context; and crafts a redirect link
that looks like it comes from this site. All three steps use the
same test target and test data, and stop at proof.

## Phase 5: fix and retest

Not run yet. Re-run only the three proofs above after fixes.

## Unvalidated

None. Every code finding reproduced live.
