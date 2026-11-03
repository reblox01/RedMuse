# RedMuse update check

You run before any RedMuse run starts, as phase 0. Your job is to
make sure the run does not use a stale tool, and to do it without
turning the tool into something nobody reviewed. Check first, update
what is safe to update automatically, and flag the rest as a
follow-up task. Never update mid-run, and never rewrite skill
content from an upstream project without a human review.

## What auto-updates, and what does not

Auto, every run, before the gate:

- RedMuse itself. If the local clone is behind origin/main, pull
  fast-forward only, then record the new HEAD in the run log. If the
  pull is not a fast-forward, stop and report it. Never force a
  pull, never rebase a user's local changes away.
- The freshness report. Record every source status in the run log,
  even when a source is unreachable.

Not auto, by design:

- RedMuse skill instructions are never rewritten from Strix,
  Securly, or Cloudflare upstream content. RedMuse does not vendor
  those projects, and its skills are original writing. A methodology
  change upstream becomes a flagged follow-up task, reviewed into a
  RedMuse commit by a human, not a silent rewrite.
- Nothing is pushed to GitHub automatically. Pushes need approval.
- Nothing updates mid-run. If an update lands while a run is going,
  finish the run on the starting version and note it, so the report
  stays reproducible.

## The check

Run tools/check_updates.sh from the RedMuse repo, or do the same
steps by hand. For each source in docs/SOURCES.md, record:

- Name and source URL.
- Local version: the commit or release the run is actually using.
  For RedMuse skills, the version is the repo HEAD commit.
- Latest available: the upstream HEAD or release at check time.
- Status: up to date, update available, unreachable, or manual.

Statuses mean:

- Up to date: local matches latest. Proceed.
- Update available, RedMuse itself: pull fast-forward, then proceed
  on the new HEAD.
- Ahead, RedMuse itself: local commits are not pushed yet. A pull
  is a no-op. Pushes still need approval, so record the ahead state
  and proceed on the local HEAD.
- Diverged: local and remote have different commits. Stop and
  report. Never force a pull.
- Unknown-relation: the fetch failed, so behind and ahead cannot
  be told apart. Record it, warn, and pull manually. Strict mode
  stops here instead of warning.
- Update available, reference source: do not rewrite anything.
  Record the delta in the run log and open a follow-up task if the
  change affects a methodology RedMuse teaches (for example a new
  OWASP Top 10 edition or a new Strix release note).
- Unreachable: record it as unreachable, warn, and proceed with the
  last known versions. A localhost demo must not fail because the
  network is down. Strict mode is the exception: if the user asked
  for strict, stop on unreachable or stale instead of warning.
- Manual: sources with no version endpoint, such as the Cloudflare
  docs behind the edge checklist. Record them as manual, never as
  a version number, and never as clean.

## Source rules

- RedMuse: git origin, auto-pull fast-forward only.
- Strix: methodology reference only, not vendored, not copied.
  Check the latest release or HEAD, flag deltas, rewrite nothing.
- Securly: optional external skill, reference only, not vendored
  in RedMuse. If the user has Securly installed, check its upstream
  HEAD against the installed copy and record both. RedMuse never
  updates the user's Securly install for them.
- Cloudflare: no bundled skill, no version endpoint. The edge
  checklist is original RedMuse writing. Review Cloudflare docs on
  major changes by hand and record the review date.

## Output

The run log gains an update check section before the gate section:

- RedMuse HEAD before and after any pull.
- One line per source: local version, latest version, status.
- Follow-up tasks opened for reference deltas, or none.
- Whether the run proceeded on the checked versions or under a
  staleness warning.

A run that skipped the update check says so in its report. A run
that proceeded under a staleness warning says so too. Neither is
reported as fully current.
