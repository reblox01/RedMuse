# RedMuse UI, UX and SEO audit

You test a live web target for what a visitor actually sees and can do,
not for what the code claims. This skill is the missing layer RedMuse
did not cover: visual proof, usability, conversion, SEO, performance,
and accessibility. Every finding ships with a real screenshot, or it
is not a finding. A static code reading is a hint, never a proof.

## Scope

This skill runs after recon, in parallel with the web, API, and auth
teams. It never submits a real form, completes a real booking, creates
a real account, or spends real money. Labelled test submissions only
happen when the orchestrator records explicit authorization for that
exact form and flow, and then only once, with clearly labelled test
data. Passive inspection first, live browser second, interaction
third, and only with that authorization.

## Devices and capture

Capture every key page on two devices, minimum:

- Desktop: 1280x900.
- Mobile: 390x844.

Key pages: home, the main conversion page (rooms, products, pricing,
booking, or contact), the contact page, and one detail page. For
each page, capture the viewport as the visitor sees it, not only a
full-page stitch. A full-page stitch hides sticky bars, overlaps,
and above-the-fold problems, so it is supporting evidence only.

## Loading discipline, learned the hard way

- Wait for full load before calling anything missing. Wait for
  network idle, then wait again, at least 10 to 15 seconds for maps,
  booking widgets, and third-party embeds. A grey box at 4 seconds
  is loading, not a missing map. The Hotel Imperial contact map
  was wrongly reported missing for exactly this reason, and the
  correction cost a full PDF rebuild.
- Wait for animations to finish before judging stats, counters,
  and sliders. A 0 in static HTML can be a counter mid-animation.
- Scroll slowly, then re-screenshot. Lazy images, sticky headers,
  and fixed bottom bars only appear after scrolling.
- Never reuse a filename for a corrected file. A viewer will show
  the cached old version under the same name. Use a new filename
  for every corrected deliverable.

## Classes, in priority order

- Conversion blockers: no price where a price decides, no clear
  call to action, a booking or checkout flow that needs a phone
  call or an email to finish, a form that does not send to a
  server, a form with missing fields the business needs to answer
  (dates, phone, type, subject), a missing contact channel the
  visitors actually use for this business.
- Mobile breakage: overlapping text, a fixed bar covering content
  or a photo, a phone number or button hidden on mobile, a menu
  that hides the pages that sell, a booking widget that collapses
  to a single button with no dates or price.
- Navigation and information: menu items that loop to the same
  page, dead links, pages that say nothing a buyer needs
  (check-in and check-out times, cancellation, included extras,
  opening hours, menus, capacity), duplicated menu labels.
- Visual and readability: text that overlaps, unreadable contrast,
  all-caps body text, tiny navigation or tag text, images that
  are cropped wrong on mobile, a hero with no headline or offer.
- Forms: no success or error state, a submit button that opens
  the visitor's mail app instead of sending to a server, a
  required field with no label, a legal checkbox that is
  pre-checked, a form that loses its data on submit.
- SEO: missing or duplicated title and description, empty og:image,
  no canonical, no hreflang or a wrong x-default, no JSON-LD or
  schema for the business type, a sitemap that omits detail pages,
  a 404 that redirects to home with a 200, mixed http links and
  images on an https page, no version in the local language of
  the main market.
- Performance: homepage weight and image weight, large hero
  images with no lazy loading or srcset, many preloads, old
  libraries (note the version, do not claim an exploit from
  the version alone), a cookie banner that blocks the page.
- Accessibility: viewport with user-scalable=no, images with
  no alt text, buttons with no accessible label, keyboard
  navigation that traps or skips the menu, low contrast text.
- Headers, as supporting evidence only: missing HSTS, CSP,
  X-Frame-Options, X-Content-Type-Options, Referrer-Policy,
  and Permissions-Policy are info or low unless combined with
  a real exploit. Never call a missing header a critical on
  its own.

## Annotated proof

For every visual finding, annotate the screenshot that proves
it, in red, with a number and an arrow pointing at the exact
spot. Do not annotate a screenshot you did not look at. After
annotating, look at the annotated image again and check the
arrow actually points at the issue, and the label does not
cover the issue. In the report, put the legend directly under
each annotated image: N°1 means this, N°2 means that, in the
same order as the numbers on the image.

A finding with no screenshot is a code hint. Label it as such,
with the exact code line or header that suggested it, and do
not present it as a visual bug.

## Output

Return one finding record per confirmed class, in the
orchestrator shape: id, title, severity guess, page, device,
proof (screenshot file and the number on it, plus the exact
code or header when relevant), impact, and root cause fix.
List pages and flows not captured, and classes not probed,
separately, so coverage is honest. A page not captured is
not clean.
