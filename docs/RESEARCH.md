# Research

How Strix works, how the wider field works, and what redmuse takes
from each. All findings below come from the public Strix repository
and docs, OWASP material, and public scanner docs. No Strix text is
copied here.

## Strix, the engine

Strix is Python on the OpenAI Agents SDK with LiteLLM, so any provider
model can drive it. The moving parts:

- Agent graph plus prompts. A root agent fans out to specialist agents,
  each with its own prompt pack, and results merge back into one run.
- Tools. Shell, browser, proxy, scanners, plus thinking, threat
  modeling, todo lists, notes, reporting, patching, MCP, web search,
  and image viewing. The agent is only as good as its tools.
- Runtime. A Docker sandbox per run, with a Caido web proxy bootstrap
  for traffic inspection. Isolation is a feature, not an afterthought.
- LLM session care. Compaction, context budgets, request logs, and
  warmup. Long runs are managed, not left to grow until they break.
- Guardrails. Model settings plus tool call limits, so a run cannot
  loop forever or spend without bound.
- Knowledge packs. Internal skills per vuln class (IDOR, CSRF, JWT,
  business logic, and more), per recon topic (asset discovery,
  infrastructure), per protocol, per framework, and per scan mode.
- Reporting. Markdown reports, one file per vulnerability, a JSON
  findings file, and SARIF 2.1.0 for ingestion into code scanning.
- Two doors. Self-hosted CLI (free, local, Docker, your own LLM key)
  and managed cloud (no Docker, no key, credits, dashboards, PR
  reviews, schedules, webhooks).

## Scan modes, what each one means

- Quick. Time-boxed, breadth over depth. High-impact targets in
  priority order: auth bypass, broken access control, remote code
  execution, SQL injection, SSRF, exposed secrets. Skip exhaustive
  enumeration and low-severity noise. Minimal proof of concept per
  finding.
- Standard. Balanced and systematic. Full recon, then business logic
  analysis (critical flows, role boundaries, data rules, state
  transitions, trust boundaries), then methodical testing per attack
  surface with focused subagents per area.
- Deep. Exhaustive. Every parameter, endpoint, and edge case, plus
  chaining findings for maximum impact. White-box adds static triage
  (semgrep, AST passes, secret scans, dependency scans) before manual
  review. Slow, thorough, and the mode that finds what others miss.
- Diff. Changed code only. Built for pull requests: review the diff,
  test what changed, block the merge on real findings.

redmuse adopts all four modes with the same meanings, scaled to
Muse-native budgets.

## White-box tooling worth knowing

Strix white-box runs lean on a small set of proven tools: semgrep for
fast static triage, ast-grep or Tree-sitter for structural mapping,
gitleaks and trufflehog for secrets, trivy for filesystem and
dependency scans, and CVE lookups for named products. redmuse treats
these as optional tier-two tools: use them when installed, note their
absence when not, and never let a missing tool silently shrink
coverage. The report must say which tools ran.

## The wider field

- Classic scanners (ZAP, Nuclei, Burp) are fast and signature based.
  They find known patterns well and prove little. Their weakness is
  false positives and no business logic understanding.
- Manual pentesting is deep and contextual, and slow and expensive.
  Its strength is chaining and logic flaws that signatures miss.
- AI pentesters (Strix and peers) sit between: agent reasoning plus
  real exploit attempts, so findings come with proof instead of
  alerts. Their weakness is cost, runaway loops, and sandbox needs.
- Passive scanners (SniffPup and peers) cover the public surface only:
  leaked keys, open files, headers, DNS. Fast, safe, and shallow by
  design. They complement active testing, they do not replace it.

redmuse positions itself as the AI pentester for Muse users: agent
reasoning plus real proofs, with the engine already in the room.

## What makes a security tool spread

Observed from Strix and peers, not promised for this project:

- Open source with a one-command install. Friction kills adoption.
- A CLI or skill that works in the user's existing flow, not a new
  dashboard to learn.
- Real proof with every finding. Screenshots and payloads beat claims.
- Sample outputs in the repo, so a visitor sees the value in a minute.
- CI integration, so the tool runs on every pull request, not once.
- A cloud option for teams that cannot run infra, beside the free
  local option.
- Docs written for agents as well as people, including an llms.txt
  style index.
- Public methodology: named classes, named modes, honest coverage
  statements. Trust spreads faster than hype.

redmuse builds all eight into v1 and v2: install script, skills for
the existing Muse flow, sample reports, CI skill, cloud handoff notes,
agent-first docs, and honest coverage in every report.

## Open questions for later versions

- SARIF export from findings.json, for GitHub code scanning ingestion.
- A container mode for untrusted targets when Docker is available.
- Scheduled runs and webhook results, mirroring the cloud feature set.
- A benchmark target suite beyond the two localhost apps, with a
  public scoreboard per release.
