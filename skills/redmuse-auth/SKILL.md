# RedMuse auth and session testing

You test authentication, sessions, and tokens for a redmuse run.
Test accounts only. Never touch real user credentials or real sessions.
Every finding ships with a reproduced proof, or it is not a finding.

## Login and reset

- Login flaws: user enumeration through error messages and timing,
  weak lockout or rate limits on test accounts, and credential
  stuffing with test credentials only.
- Password reset: tokens that leak validity, reset links that work
  without the token, and reset flows that accept another user's
  identifier.
- Signup flaws: duplicate accounts, role fields accepted at signup
  (mass assignment into role), and email verification bypass.

## Sessions and tokens

- Session fixation: a session id issued before login that stays valid
  after login.
- Session expiry: tokens that never expire, logout that does not
  invalidate the server side, and refresh tokens with no rotation.
- JWT flaws: none algorithm accepted, weak secrets (test only against
  a local or staging instance with permission), algorithm confusion,
  missing expiry, and claims the server trusts without verification
  (role, admin, tenant).
- Cookie flags: missing HttpOnly, Secure, or SameSite on session
  cookies. Info level alone, higher when combined with an XSS or a
  session flaw.

## Abort and TOCTOU in async session code

- Name the exact await, not the check-to-call gap. In async JS, a
  check followed by adjacent synchronous statements has no window
  for an abort to land in: no signal can be delivered between two
  synchronous statements. The real window is during or after an
  awaited operation, for example the awaited INSERT that creates
  the session row. A TOCTOU finding must name that await and the
  state that can change across it. A fix that only re-checks before
  the call is not a fix; the fix must handle the post-await state,
  for example deleting the row that was already committed when the
  abort lands after the INSERT.
- Abort probes must record the client outcome next to the DB count.
  Counting session rows per user without distinguishing outcomes
  conflates a legitimate session (client got a 201) with a true
  orphan (client aborted). Log outcome-per-trial, aborted vs status
  received, alongside the row count, so an orphan count means
  aborted trials that still left a row.
- An abort guard after a synchronous DB write is only as good as
  the event-loop yields around it. On SQLite the INSERT is
  synchronous, so a post-INSERT abort check with no intervening
  yield can never observe a disconnect that lands mid-INSERT; the
  check needs an explicit timer yield (or an async DB call) to see
  it. Flag "abort guard after a sync DB write without an
  intervening yield" as a review finding, and prove it with a
  lock-held repro, not a sleep-based probe alone: hold the DB write
  lock (or otherwise stall the sync write), abort during the stall,
  then assert 0 orphan rows. A sleep-based probe alone cannot
  distinguish "guard works" from "guard works only when something
  yields".
- Require a lock-held repro on the PRE-fix commit, not just the
  fixed code. A diff-only review cannot show whether the old guard
  was dead on SQLite; the contrast between the pre-fix run (for
  example orphans on 2 of 2 aborted trials) and the post-fix run
  (0 of 7) is what proves the yield fixed it. Record both runs.
- Ownership: this section names the finding rule. The full
  widened-window recipe lives in redmuse-orchestrator,
  redmuse-fix owns retesting after a patch, and redmuse-verify
  independently re-proves a fix with the recipe in redmuse-verify.
  A finding from this section names the exact await so the other
  two can run the recipe without guessing it.

## Password audit

- Policy, against NIST 800-63B: minimum length 8, no forced
  complexity rules that push users to weak patterns, no
  password expiry without a reason, and a blocklist of
  breached and common passwords. A policy that requires a
  special character but allows `Password1!` is a finding
  about the policy, not about the user.
- Strength-bar probes must use forms of 8 characters or more.
  A 6- or 7-character probe is meaningless for the strength
  bar because the length rule fires first and masks every
  other rule; a "live" result from a short probe proves
  nothing about the walk, pattern, or denylist rules. Always
  use >=8-character forms, and re-check node-harness results
  for length before concluding a probe passed or failed.
- Walk matchers work on 6-character windows, so any walk
  whose 6-windows are individually innocent is structurally
  invisible to them. Probe 8-12 character walks whose every
  6-window looks innocent, not just longer versions of known
  6-window walks: bridges across keyboard rows, interleavings
  of two short walks, and pair structures (for example
  alternating hands or repeated pairs) that never form a
  flagged 6-window.
- Exact-match denylists need a repeated-form variant check.
  Doubling bypassed both the common-password list and the
  email-local equality check alike: a doubled form of a
  denied value is not an exact match, so it passes. At review
  time, ask of any exact-match denylist "what does the
  doubled form do?" and probe the doubled, tripled, and
  case-varied forms of each denied value.
- Storage and hashing: bcrypt, scrypt, or Argon2 with a cost
  that is not the minimum, and a unique salt per password.
  MD5, SHA-1, or plain SHA-256 of a password with no salt,
  or a single global salt, is a finding. The hashing code
  is the proof, never crack a real password to prove it.
- Breach exposure: check whether test accounts use passwords
  that appear in known breaches, using a k-anonymity lookup
  or a local blocklist, never by sending a real password to
  a third party in full. A test password that appears in a
  breach list is a finding about the policy, not about the
  person.
- Lockout and rate limits: a login that allows unlimited
  guesses on a test account, a lockout that locks the real
  user out instead of the attacker, and a reset flow that
  does not rate limit. Test with dummy accounts only, and
  record the attempt count that proved the limit, or its
  absence.
- Live-probe setup for register and login rate limits: a
  per-IP bucket (for example 5/hr per IP) blocks repeated
  probes unless each attempt uses a distinct client IP. First
  establish the normal rate-limit baseline using genuine source
  IPs: run the attempts from distinct real source IPs (or one IP,
  counting attempts until the limit fires) and record the attempt
  count that triggers the limit, or its absence. Only then test
  spoofable forwarding headers as a separate, explicitly recorded
  security check: repeat the probe with a distinct X-Forwarded-For
  value per attempt and record whether the limit is bypassed. A
  bypass is a finding about trusting an untrusted forwarding
  header, not probe setup. Never present X-Forwarded-For spoofing
  as ordinary probe hygiene, and do not burn the bucket and then
  misread the resulting 429s as a target failure.
- Probe hygiene: rate-limit budgets are per-IP per-window, so
  probe IPs must be unique per invocation, not just per
  process. A per-process IP counter restarts every run and
  silently re-burns the same bucket, for example the 5/hr
  register bucket. Generate a fresh unique IP per probe
  invocation (for example from the run id and trial number)
  and log the IP used per trial.
- E2E users: seed them with a generated strong password from
  the first attempt. The strength bar rejects common
  passwords, and each rejected attempt burns budget in the
  register rate limit (in-memory, reset by server restart).
  Between debug runs, restart the server to reset the
  rate-limit buckets instead of retrying against a burned
  bucket.

## Privilege boundaries

- Vertical escalation: a low-privilege token calling admin or staff
  actions, including hidden parameters and headers that switch roles.
- Horizontal escalation: one test user's token reading or changing
  another test user's data. Coordinate with the web and API teams so
  the same flaw is not reported twice under two names.
- Tenant isolation: cross-tenant reads or writes in multi-tenant
  apps, using two test tenants.

## Identity federation (thin coverage)

Identity federation procedures in this skill are thin. There is
no full section here for OAuth 2.0, OIDC, or SAML, and no
federation probe is defined in this skill. A full section must
cover: authorization-flow tests with test accounts, PKCE,
redirect URI validation, token audience and issuer validation,
SAML assertions, and federation trust boundaries. Until that
section exists, do not improvise federation probes; record
federation flows as untested, with the reason, and do not report
them as clean.

## Output

Return one finding record per confirmed flaw, in the orchestrator
shape: id, title, severity guess, endpoint, method, parameter, proof
(exact request and response), impact, and root cause fix. Note which
auth flows were probed clean, and which ones the run could not test
for lack of a test account.
