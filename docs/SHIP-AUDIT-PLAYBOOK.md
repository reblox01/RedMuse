# Ship-ready website audit playbook

How to take a website you own, extract every bug that matters,
fix it, retest it, and ship it to a client in good health.

This playbook combines two things that were separate until now:
RedMuse for security, and the manual visual method used for
Raleyan and Hotel Imperial for UI, UX, SEO, and conversion.
The visual method is now a RedMuse skill too:
`skills/redmuse-ui/SKILL.md`.

## 0. Gate: send these before any work starts

No run starts without all of these, in the user's own words:

- Target URL, exact, live and staging if it exists.
- Repo URL and branch, if code is in scope.
- Ownership and authorization: "I own this site, test it", plus
  what is allowed: passive only, or active testing, or test
  form submissions, or test bookings.
- Scope in and out: which pages, features, and systems.
  Booking engine, PMS, payment, admin panel, and third-party
  services are out by default until named.
- Test account, if login is in scope. Never a real user account.
- What the site must do for the client: sell rooms, take
  bookings, take leads, sell products, or inform. This decides
  what counts as a conversion blocker.
- Branding for the report: Atlas Flow logo and name as a header
  on every page only, no tagline, no extra startup content,
  same as the Raleyan and Hotel Imperial reports.
- Language for the report: French by default for Moroccan
  clients, unless the user says otherwise.

A past authorization is not authorization for a new target.
A general "test it" is not authorization for active probes,
form submissions, or bookings.

## 1. Phase 0: RedMuse update and install

- Run `redmuse-update` first. Record RedMuse HEAD before and
  after. Nothing updates mid-run.
- Install the pack from https://github.com/reblox01/RedMuse,
  or use the local copy in `~/workspace/redmuse`.
- Record the run in `redmuse-runs/<site>-<date>/run-log.md`:
  target, scope, mode, budgets, authorization.

## 2. Phase 1: Recon, passive first

Run `redmuse-recon` and `redmuse-cve-intel`.

- Inventory: pages, sitemap, robots.txt, headers, server,
  libraries and versions, third-party services (booking,
  payment, maps, analytics), emails and phones in public.
- CVE intel from fingerprints, before any exploit team.
  Patched versions get no probe. Unknown versions get no
  exploit attempt.
- Data leak sweep: crawl the public pages, look for API keys,
  tokens, passwords, and secrets. A hit from a CSS class name
  is a false positive until proven otherwise, record it as such.

## 3. Phase 2: Code dev-audit, if the repo is in scope

Run `redmuse-dev-audit`, code first, then live proof.

- `redmuse-code` white-box review on the repo.
- Write a harmless exploit scenario per finding.
- Run it on localhost or staging only, with test data.
- Then `redmuse-fix`, then retest the same scenario.
  A fix that is not retested is not closed.

If there is no repo, skip this phase and say so in the
coverage statement. Do not call the code clean.

## 4. Phase 3: Live security, only if authorized

Run `redmuse-web`, `redmuse-api`, and `redmuse-auth`.

- Web: OWASP Top 10, harmless markers only, one variable
  at a time, test accounts only.
- API: OWASP API Top 10, same discipline.
- Auth: login, session, privilege boundaries, rate limiting
  only up to the agreed number of attempts, with a dummy
  user, never a real password.
- Every finding needs a reproduced proof, or it is not a
  finding. Probed-but-clean classes are listed separately.
- Never touch real user data, real sessions, or live
  payment. Never pivot past proof of reachability.

## 5. Phase 4: UI, UX, and visual proof

Run the new `redmuse-ui` skill. This is the Raleyan and
Hotel Imperial method, written down.

- Capture home, main conversion page, contact, and one
  detail page, on desktop 1280x900 and mobile 390x844.
- Wait for full load: network idle, then 10 to 15 seconds
  more for maps, booking widgets, and embeds. A grey box
  at 4 seconds is loading, not a missing map.
- Scroll slowly, re-screenshot, check sticky and fixed bars.
- Check every form and flow by reading it, and by clicking
  it only when authorized, once, with labelled test data.
- Annotate every visual finding in red, with a number and
  an arrow on the screenshot, then look at the annotated
  image again to check the arrow points at the issue.
- Legend directly under each image, in the same order.

Classes, in order: conversion blockers, mobile breakage,
navigation, readability, forms, SEO, performance,
accessibility, headers as supporting evidence only.

## 6. Phase 5: SEO, performance, and business checks

- Titles and descriptions unique per page, og:image present,
  canonical, hreflang and x-default correct, JSON-LD or
  schema for the business type, sitemap complete, 404 is a
  real 404, no mixed http on https, local language present.
- Prices where a price decides, contact channels the
  visitors actually use, check-in and check-out times,
  cancellation, included extras, opening hours, menus,
  capacity. If the buyer must call to learn it, it is a
  finding.
- Page weight, hero image weight, lazy loading, old
  libraries noted with version, cookie banner behaviour.

## 7. Phase 6: Report, like Raleyan and Hotel Imperial

Use `redmuse-report` for ranking and dedupe, then build
the client PDF in the same design as the Raleyan v3
report, with the Atlas Flow header on every page only.

Report order:

1. Cover: site, date, method, scope, authorization.
2. Synthesis table: N, problem, severity, proof.
3. One section per problem group, with annotated
   screenshots and a legend under each image.
4. What is already good, verified, not assumed.
5. Automation and next steps, in phases, with what
   needs the client's PMS, booking engine, or
   payment provider confirmed before a quote.
6. Coverage statement: what was probed, what was
   not probed and why, and whether the run was
   complete or partial. A partial run is never
   called clean.

Severity by reachability first, then impact. Merge
findings that share a root cause. Never inflate the
count with the same bug on ten pages.

## 8. Phase 7: Fix and retest, then ship

- Fix one finding at a time, with `redmuse-fix`.
- Retest only the original proof for each fixed finding.
  Record fixed, still open, or changed. Never rewrite
  history.
- Use a new filename for every corrected deliverable.
  Reusing a filename shows the cached old version.
- Ship gate, all must be true before the site goes to
  the client:
  - No critical open, no high open.
  - Every high and medium has a retest proof, not
    just a code change.
  - Desktop and mobile captures after the fix show
    the fix, with no new overlap or breakage.
  - Booking, contact, and payment flows, if in
    scope, were tested end to end with test data.
  - Report coverage statement is complete and honest.

## What RedMuse covers, and what it does not

Covered by RedMuse: recon, CVE intel, web OWASP Top 10,
API Top 10, auth, code, dev-audit, fix, CI gate, report,
MCP layer.

Covered by the new redmuse-ui skill: visual UI and UX,
mobile breakage, conversion, SEO, performance,
accessibility, annotated screenshot proof.

Not covered by either, and still manual: business
decisions (prices, offers, PMS choice), legal text,
content in the client's language, and any system the
client has not given access to. Those are listed as
open questions in the report, never guessed.

## Lessons that cost a rebuild

- Hotel Imperial map: first screenshot at 4 seconds
  showed grey, reported missing, wrong. Wait 15 seconds.
- Raleyan stats: static HTML showed 0, real browser
  showed the counters animating. Wait for animation.
- Raleyan and Hotel Imperial PDFs: overwriting the
  same filename showed the cached old version to the
  user. New filename for every corrected file.
- Header branding: Atlas Flow logo and name only, on
  every page. Adding tagline, services, or a closing
  page was rejected twice. Keep it to logo and name.
- Short replies: the user asked for less text, not
  less proof. Keep the chat short, put the detail
  in the PDF.
