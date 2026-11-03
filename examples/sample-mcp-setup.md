# Sample MCP setup (phase 0.5)

Worked example, localhost run. No real target, no key, no secret is
shown here. The point is the record: what was offered, what was
accepted, and what not run means.

## Offers, one at a time

- SniffPup, passive hosted scan, no key: not offered for this run.
  Reason: the target is localhost, not a public site, so a hosted
  public scanner has nothing to scan. Recorded as not run, not clean.
- Context7, docs lookup, hosted: accepted. Verified by tool list.
  Used in recon and code for framework behavior, never for a probe.
- next-devtools, local dev-server inspection, no key: accepted.
  Verified by tool list plus one read-only call against the running
  local dev server. Used in dev-audit only.
- cybersecurity MCP, NVD lookup, no key: accepted. Verified by tool
  list. Used in CVE intel beside tools/cve_lookup.py, under the
  same applicability rules: version ranges decide, candidates stay
  needs-confirmation, patched versions get no probe.
- A keyed MCP, generic example: offered, user declined. Setup
  stopped at the ask, no walkthrough given, no key requested.
  Recorded as declined, not run, not clean.

## Tool calls in this run

- Localhost, fake data, so active tools were callable with harmless
  markers and test data. The same MCPs on a live production target
  would have been called passively only: docs, CVE lookup, and
  harmless-marker checks, no writes, no submissions, no
  state-changing exploit.
- Every MCP call that touched the target counted against the probe
  budget. Docs and CVE lookups were logged but did not count
  against the target budget.
- One MCP result confirmed a candidate found by a built-in skill
  and was listed in confirmed_by. No finding in this example rests
  on an MCP result alone, so no finding moved from weak to
  confirmed on MCP evidence alone.

## Report lines this setup produces

- MCPs: Context7 accepted, next-devtools accepted, cybersecurity
  accepted, SniffPup not run (localhost, no public surface),
  keyed MCP declined.
- Coverage matrix: one row per MCP layer, marked probed or not run
  with the reason. No not-run row is reported as clean.
