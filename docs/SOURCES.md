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

- Source: https://github.com/cloudflare/security-audit-skill
- What it is: upstream security-audit skill (MIT), reference only.
  Correction to an earlier RedMuse note: this skill does exist
  upstream; it was only missing from the local collection. RedMuse
  does not bundle it, and the edge checklist in redmuse-dev-audit
  stays original RedMuse writing. When the skill is installed, use
  it as an additional layer.
- Version: upstream HEAD commit at check time.
- Check: upstream HEAD via the public repo.
- Auto-update: no. A delta becomes a follow-up task.
- CLI: none. The skill is guidance, not a tool wrapper.

## Sentry

- Source: https://github.com/getsentry/skills (Apache-2.0)
- Covers: security-review (high-confidence code review, OWASP
  cheat sheet based, report only what is confidently exploitable),
  gha-security-review (GitHub Actions workflow exploitation, every
  finding needs a concrete exploitation scenario), security-model
  (SECURITY_MODEL.md policy context for scoping what counts as a
  finding).
- Version: upstream HEAD commit at check time.
- Check: upstream HEAD via the public repo.
- Auto-update: no. A delta becomes a follow-up task.
- CLI: none. Agent tools only (Read, Grep, Glob, Bash, Task).

## OWASP

- Source: https://github.com/agamm/claude-code-owasp (MIT)
- Covers: owasp-security (OWASP Top 10:2025, ASVS 5.0, LLM Top 10
  2026, Agentic Top 10 2026, with per-language and config
  checklists).
- Version: upstream HEAD commit at check time.
- Check: upstream HEAD via the public repo.
- Auto-update: no. A delta becomes a follow-up task.
- CLI: none. The skill is checklists and review workflow.

## Masriyan cybersecurity collection

- Source: https://github.com/Masriyan/Claude-Code-CyberSecurity-Skill
  (MIT, version 3.3.0, 22 skills total)
- Covers, picked 5 of 22: 01-recon-osint, 02-vulnerability-scanner,
  08-network-security, 09-web-security, 16-ai-llm-security. These
  skills require authorized scope themselves and separate observed,
  inferred, and unverified evidence.
- Version: upstream HEAD commit at check time.
- Check: upstream HEAD via the public repo.
- Auto-update: no. A delta becomes a follow-up task.
- CLI: nmap, nuclei, trivy, ZAP, sqlmap, tshark, Suricata, Snort,
  Zeek, plus the collection's own Python script CLIs (Python 3.10+,
  full plugin checkout). None of these external CLIs are installed
  on the demo VM, so those paths are dormant there. Availability
  is checked on the run machine, never claimed without that check.

## Trail of Bits

- Source: https://github.com/trailofbits/skills (CC-BY-SA-4.0,
  Claude Code plugin marketplace)
- Covers: semgrep, codeql, sarif-parsing (static-analysis plugin),
  differential-review, variant-analysis. Found through the
  agenticskills.io security directory and verified against the repo.
- Version: upstream HEAD commit at check time.
- Check: upstream HEAD via the public repo.
- Auto-update: no. A delta becomes a follow-up task.
- CLI: semgrep, codeql. Neither is installed on the demo VM; check
  on the run machine. Reference only, never copied, which the
  share-alike license also requires.

## OpenAI codex-security

- Source: https://github.com/openai/codex-security (Apache-2.0)
- Covers: threat-model, security-diff-scan, validation. This is
  the open skill repo, not the Codex Security Cloud SaaS product,
  which is a separate paid workflow and is not tracked.
- Version: upstream HEAD commit at check time.
- Check: upstream HEAD via the public repo.
- Auto-update: no. A delta becomes a follow-up task.
- CLI: none.

## Considered, not added

- Sentry django-access-review (Django-specific), find-bugs,
  code-review (generic; the RedMuse code skill covers the job).
- Masriyan 03-exploit-development, 04-reverse-engineering,
  05-malware-analysis, 06-threat-hunting, 07-incident-response,
  10-cloud-security, 11-csoc-automation, 12-log-analysis,
  13-crypto-analysis, 14-red-team-ops, 15-blue-team-defense,
  17-mobile-security, 18-ot-ics-security, 19-grc-compliance,
  20-supply-chain-security, 21-threat-intelligence,
  22-purple-team: different disciplines, niche stacks, or already
  covered by the picked five. Exploit-development in particular
  goes beyond RedMuse's proof-of-concept on an authorized target.
- agenticskills.io smart-contract scanners (Algorand, Cairo,
  Cosmos, Solana, Substrate, TON) and other directory entries
  (Azure Key Vault, Varlock, REA, ClawSec, Audit Website): niche
  stacks or repos not verified from the directory page. The
  directory itself is a listing, not a git source, so it is not a
  tracked entry. The Trail of Bits and OpenAI entries above came
  from that directory and were verified against their repos.

## CLI availability

The cli field in sources.yaml names tools the skills use. It is
not a claim they are installed. The run machine checks
availability before any CLI path is used. If a CLI is missing,
that path is skipped and recorded, never faked.
