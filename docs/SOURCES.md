# Sources RedMuse tracks

Machine-readable registry: skills/redmuse-update/sources.yaml.
That file is authoritative for the update check script; this doc
explains the same sources in prose.

RedMuse is a skill pack with original writing. It does not vendor
Strix, Securly, or Cloudflare skills, and it never copies their
content. This registry exists so the pre-run update check in
skills/redmuse-update can say, for each reference, what version was
checked and whether anything changed. If a source is not listed
here, the update check does not track it.

## RedMuse itself

- Source: https://github.com/reblox01/RedMuse
- What it is: this repo, all RedMuse skills, docs, templates,
  tools, and test targets.
- Version: the git HEAD commit of the local clone.
- Check: compare local HEAD with origin/main HEAD.
- Auto-update: yes, fast-forward pull only, before the run starts.
  A non-fast-forward pull stops and reports instead of forcing.
- Auto-push: no, pushes need approval.

## Strix methodology

- Source: https://github.com/usestrix/strix
- What it is: methodology reference only. RedMuse is inspired by
  Strix architecture (agent graph, skill packs, sandbox runtime,
  SARIF-style reporting) and credits it. No Strix code or skill
  text is copied into RedMuse.
- Version: latest Strix release or HEAD commit at check time.
- Check: latest release or HEAD via the public repo.
- Auto-update: no content rewrite. A methodology delta is flagged
  as a follow-up task and reviewed into a RedMuse commit by a human.

## Securly

- Source: https://github.com/BghitCode/Securly
- What it is: optional external skill, reference only. The
  redmuse-dev-audit skill uses the Securly audit checklist as a
  rubric for AI, agent, and mobile targets. Securly is not vendored
  in RedMuse.
- Version: upstream HEAD commit, compared with the installed copy
  when the user has Securly installed.
- Check: upstream HEAD via the public repo.
- Auto-update: no. RedMuse never updates the user's Securly
  install. It records both commits when both are known.

## Cloudflare

- Source: Cloudflare documentation (no single repo, no version
  endpoint).
- What it is: background for the original Cloudflare edge
  checklist in redmuse-dev-audit. There is no bundled Cloudflare
  skill in RedMuse, and the checklist text is original RedMuse
  writing.
- Version: none. Recorded as manual, with the last review date
  when a human reviewed the docs.
- Check: manual review of Cloudflare docs on major changes.
- Auto-update: no. Never report a Cloudflare version number, and
  never report the checklist as clean because a check ran.
