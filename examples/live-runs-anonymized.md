# Live runs, anonymized proof

RedMuse tested on real, authorized targets on 3 Nov 2026, not only on the
intentionally vulnerable localhost demos. This file is the public proof of
those runs, with targets anonymized.

## Anonymization rule

No target is named here. No domains, no repository names, no URLs, no
credentials, no exploit payloads, and no distinctive internal identifiers
are included. Targets are labeled Site A, Site B, Site C, Repo A, and
Repo B. Finding titles below are vulnerability classes, not target
details. Full private reports stay with the target owners.

Tool version at run time: RedMuse at commit 35f03bb. Phase 0 update
check passed on every run: RedMuse up to date, all 13 reference sources
unchanged, no skill rewritten, nothing pushed during a run.

Rules followed on every run: authorized targets only, harmless markers
only, no destructive payloads, no real credentials, no account creation,
no form submissions that write data, no exploit attempt on the PHP
runtime question below, repo clones deleted after audit, nothing
committed or pushed to any target repository.

## Summary

Times are Africa/Casablanca (UTC+1). Probe budgets are quick mode only.

| Run | Date and time | Mode | Target type | Result |
|---|---|---|---|---|
| Site A | 3 Nov 2026, 14:30 | Quick, 37 of 50 probes | Personal portfolio site, modern web stack | 0 critical, 0 high, 0 medium, 0 low, 3 info |
| Site B | 3 Nov 2026, 14:31 | Quick, 23 of 50 probes | Agency site, modern web stack | 0 critical, 0 high, 0 medium, 0 low, 5 info |
| Repo A | 3 Nov 2026, 14:33 | Dev-audit, code phase only | JS portfolio codebase with dashboard | 0 critical, 1 high, 2 medium, 3 low, 1 info |
| Repo B | 3 Nov 2026, 14:33 | Dev-audit, code phase only | PHP blog codebase with author and admin roles | 0 critical, 0 high, 2 medium, 3 low, 2 info |
| Site C | 3 Nov 2026, 18:19 | Quick, 33 of 50 probes | Production PHP login application | 0 critical, 1 high, 0 medium, 2 low, 3 info |

Totals across the 5 runs: 0 critical, 2 high, 4 medium, 8 low, 14 info.
One major question was left honestly unvalidated, see Site C.

## Site A: personal portfolio site

Scope: public surface only. No login, no form submission, no account.

Found, all info, all confirmed live:
- Content Security Policy allows unsafe-inline and unsafe-eval. The rest
  of the policy is strong, so this is hardening only.
- CORS wildcard on responses. No sensitive GET API was found, so no
  cross-origin read was demonstrated.
- Missing security.txt, so no stated disclosure channel.

Checked clean: reflected XSS marker not reflected, open redirect
attempts did not redirect, sensitive files returned 404, the image
optimizer enforced its domain allowlist, HTTP redirected to HTTPS.

Not tested, listed as gaps, never as clean: authenticated areas,
session handling, login lockout, contact form submission, stored and
DOM XSS, SQL injection, full script bundle crawl, TLS certificate
details.

## Site B: agency site

Scope: public surface only. No login, no form submission, no account.

Found, all info, all confirmed live:
- Missing security headers (only transport security and CORS present).
- Wildcard CORS. No cookies or auth exist on the site, so no credential
  risk was demonstrated.
- Transport security set without subdomain coverage or preload.
- Email authentication monitoring only (DMARC policy set to none, no
  reporting address).
- Two conflicting soft-fail sender records for the same domain, which is
  a protocol violation for receivers.

Checked clean: reflected markers not reflected, sensitive files
returned 404, GET on the contact API correctly rejected.

Not tested, listed as gaps, never as clean: contact form submission
behavior (validation, rate limiting, email sending, CSRF enforcement),
browser-based exploitation, file upload or export, TLS certificate
details, remaining public pages and script chunks not fetched in quick
mode.

## Site C: production PHP login application

Scope: public surface only. Login page checked by presence, plus 3 dummy
login attempts with fake credentials, no lockout warning seen. No
successful login, no test account, no data written.

Found, all confirmed live:
- High: deployed version-control directory publicly browsable, including
  its listing, config, and HEAD reference. Source and history can be
  reconstructed from the web server even though the code repository
  itself is not public. History objects were deliberately not
  downloaded, so whether history contains secrets was not assessed.
  Fix: remove the directory from the web root, block all dot-directories
  in server config, audit the exposed history for secrets, rotate
  anything found.
- Low: directory listing on an application directory, revealing file
  names only. Application files execute rather than serve source, so
  low alone, supporting the high above.
- Low: login form carries no anti-CSRF token, in the form or in the
  login request fields.
- Info: missing Content-Security-Policy header, while the rest of the
  header set is good.
- Info: transport security set without preload.
- Info: login captcha fallback reaches backend processing. When the
  captcha script is unavailable, the page sends a fallback value, and a
  fake login with that value reached database handling and returned a
  database connection error, not a captcha rejection.

Checked clean: reflected XSS marker not reflected, open redirect
parameters did not redirect, unauthenticated app page redirected to
login, database endpoint with a fake user returned 403 with no data
leaked, HTTP redirected to HTTPS, no wildcard CORS header.

### PHP runtime question: unvalidated, not patched, not vulnerable

The run was asked whether the server had fixed the two critical PHP
runtime flaws disclosed 21 Oct 2026, CVE-2026-109618 and CVE-2026-109619,
both rated CVSS v4.0 9.2, fixed in PHP 8.5.12, 8.4.27, 8.3.36, and
8.2.35. This could not be answered from outside, and no exploit was
attempted, by design: those flaws allow remote code execution and an
exploit attempt can crash or corrupt a production server.

Evidence checked, all negative for version exposure: no version header
on any response, version-info and package-manifest paths returned 404,
error pages were generic server pages with no version, page code
confirmed a PHP runtime but carried no version string, session cookie
name was custom, not a version leak.

What closes it: check the server directly for the installed PHP version,
confirm the branch is at or above the fixed release or carries a vendor
backport, and restart PHP processes after any update. Until that check
is done, the status stays unvalidated. It is never reported as patched
and never reported as vulnerable on version evidence alone.

Not tested, listed as gaps, never as clean: authenticated access
control, session behavior after login, login enumeration and lockout
beyond 3 dummy attempts, stored and DOM XSS, SQL injection, command
injection, file upload or export, full script crawl, TLS certificate
details, dependency versions beyond fingerprinting.

## Repo A: JS portfolio codebase with dashboard

Scope: dev-audit, code phase only, read-only. No live proof was possible
without auth and database credentials, so every finding below is weak
(code-traced only), never confirmed. No fixes applied, no retest run.

Found:
- High: missing admin authorization. Middleware and server actions
  checked authentication only, not admin role. Dashboard layout had no
  auth check, and admin actions and API routes checked only a user id.
  Since sign-up was public with no allowlist found in code, any
  authenticated registrant could use the full dashboard. Caveat
  recorded: sign-up restrictions set in the auth provider dashboard
  itself are not visible from code and would lower this severity.
- Medium: email credentials stored in plaintext and returned by getter
  actions, even though the UI only shows a configured badge.
- Medium: contact email origin check skipped when the Origin header is
  absent, so script requests pass it. Recipient is fixed to the owner,
  so this is spam and mail abuse, not an open relay.
- Low: rate-limit identity taken from a spoofable forwarded-for header.
- Low: unauthenticated encryption for AI keys with a fixed salt and no
  message authentication code. Tampering fails closed, so hardening.
- Low: stored javascript: URL possible in project links, chained on the
  high above.
- Info: Content Security Policy includes unsafe-eval.

Checked clean in code: parameterized queries, output sanitization
allowlists, good security headers, AI keys server-side only.

Not covered, listed as gaps, never as clean: live proof, edge checklist
(no staging domain), dependency CVE scan (versions noted only), CI and
diff review, production auth provider settings.

## Repo B: PHP blog codebase with author and admin roles

Scope: dev-audit, code phase only, read-only. No live proof was possible
without a PHP and database setup, so every finding below is weak
(code-traced only), never confirmed. No fixes applied, no retest run.

Found:
- Medium: stored XSS through a post description field with only a
  required-field check, rendered raw in two templates. Requires an
  author role granted by an admin, hence medium, not high.
- Medium: no CSRF protection on raw POST routes, covering role change,
  user delete, post status and delete, annotation actions, and profile
  and password updates with no current-password check. Mitigated in
  practice by SameSite Lax session cookies, hence medium, not high.
- Low: no login throttling configured.
- Low: committed secret values in development environment files.
  Production uses a generated secret and separate config, so this
  appears development-only. Rotate if any committed value was ever
  reused in production.
- Low: uploaded image content type taken from the client claim and
  served verbatim, so a crafted upload could execute script on direct
  navigation. Requires an author role plus direct navigation.
- Info: base64 image path with no size limit or content validation,
  unlike the 5 MB limit on form uploads.
- Info: route-level access control fully commented out. Defense in
  depth only, per-action checks currently cover admin and author
  routes.

Checked clean in code: per-action role checks plus author ownership
checks, self-delete blocked, deletes POST-only, registration fixed to
the base user role, escaped comments, parameterized queries only, image
encryption with authentication code and random IV, profiler
development-only with production config in deploy settings, request
logger logging no bodies or headers, form CSRF present on framework
form routes.

Not covered, listed as gaps, never as clean: live proof, edge checklist
(no staging domain), dependency CVE scan (framework version pinned,
currency not verified), CI and diff review, production runtime config
beyond the repository.

## How to read this file

A partial run is never called clean. A code-only finding is never
called confirmed. An unvalidated item is never called patched and never
called vulnerable. That discipline is part of the proof: the tool
reports what it proved, what it checked clean, and what it could not
check, in separate lists.
