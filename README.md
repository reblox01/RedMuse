# RedMuse

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Engine: Muse](https://img.shields.io/badge/Engine-Muse-blue.svg)](https://muse.ai)
[![Docker: none](https://img.shields.io/badge/Docker-not%20required-brightgreen.svg)](docs/ARCHITECTURE.md)
[![LLM key: none](https://img.shields.io/badge/LLM%20key-not%20required-brightgreen.svg)](docs/ARCHITECTURE.md)

Muse-native autonomous pentesting, built for Muse. No Docker, no LLM
key, no separate engine. Muse is the engine: an orchestrator plus
specialist agents run recon, exploitation, proof-of-concept validation,
fixing, and reporting against targets you own or are authorized to
test.

Inspired by the architecture of [Strix](https://github.com/usestrix/strix)
(agent graph, skill packs, sandbox runtime, SARIF-style reporting),
rebuilt from scratch as skills and playbooks that any Muse user can
install and run. Skill content here is original writing. Strix itself
is Apache-2.0, and its methodology topics (OWASP Top 10, API Top 10,
IDOR, SSRF, and friends) are credited in `docs/ARCHITECTURE.md`.

## Quick start

```bash
git clone https://github.com/reblox01/redmuse.git
cd redmuse
./scripts/install.sh
```

Then, in Muse:

```text
Run redmuse-orchestrator against https://staging.example.com, mode quick.
I own this target and authorize active testing on it.
```

The orchestrator records the authorization gate first, then runs the
phases and writes the report. No active test runs without the gate.

## What is inside

9 skills, one per job:

- redmuse-orchestrator: the gate, the teams, the budgets, validation
- redmuse-recon: attack surface inventory, passive first
- redmuse-web: OWASP Top 10, black-box
- redmuse-api: OWASP API Security Top 10
- redmuse-auth: login, session, JWT, privilege boundaries
- redmuse-code: white-box data-flow review
- redmuse-report: severity, dedupe, honest coverage, retest
- redmuse-fix: root cause patch plus retest loop
- redmuse-ci: diff-scoped merge gate for GitHub Actions

Plus:

- `docs/RESEARCH.md`: Strix deep dive, scan modes, field landscape,
  what makes a security tool spread
- `docs/ARCHITECTURE.md`: Strix-to-Muse mapping, scan modes, team
  protocols, tool tiers, report schema, sandbox modes
- `docs/SAFETY.md`: the authorization gate and the rules that are part
  of the tool
- `templates/`: finding, report, and run log templates
- `tools/render_report.py`: findings.json to standalone HTML report
- `test-target/` and `test-target-api/`: intentionally vulnerable
  localhost apps, fake data only, never deploy them publicly
- `examples/`: real sample reports from localhost runs

## Scan modes

| Mode | Meaning | Probes | Time | Teams |
|---|---|---|---|---|
| quick | Breadth, high-impact targets first | 50 | 30 min | 3 |
| standard | Full recon, business logic, methodical testing | 150 | 2 h | 3 |
| deep | Every parameter and edge case, chained findings | 300 | 4 h | 5 |
| diff | Changed code only, for pull requests | 100 | 1 h | 2 |

## Proven on localhost

Web test target, quick run: 2 high (IDOR, API BOLA), 1 medium
(reflected XSS), 1 low (open redirect), 1 info (missing headers). All
reproduced live. See `examples/sample-report-localhost.md`.

API test target, quick run: 2 high (BOLA, mass assignment), 2 medium
(admin bypass, excessive data exposure). All reproduced live. See
`examples/sample-report-api.md`.

## How it compares

| | redmuse | Strix CLI | Strix Cloud | ZAP / Nuclei |
|---|---|---|---|---|
| Engine | Muse itself | Any LLM via key | Hosted | Signatures |
| Infra needed | None | Docker | None | Local binary |
| Cost | Free | LLM key cost | Credits | Free |
| Findings | Proved with PoC | Proved with PoC | Proved with PoC | Alerts, often unproved |
| Sandbox | Workspace | Fresh container | Hosted | None |
| Best for | Muse users, fast | Full local control | Teams, schedules | Quick signature scans |

Honest limits: the workspace is the sandbox, not a fresh container per
target, and one brain with subagent teams is less parallel than a true
model swarm. Coverage statements in every report say exactly what was
and was not probed.

## Safety

Read `docs/SAFETY.md` before your first run. The short version: only
test targets you own or are authorized to test, passive first, active
probes only after the authorization gate, non-destructive payloads
only, test accounts only, secrets masked in every report.

## Roadmap

- SARIF export from findings.json for GitHub code scanning
- Container mode for untrusted targets when Docker is available
- Scheduled runs and webhook results
- A benchmark target suite with a public scoreboard per release

## Contributing

See `CONTRIBUTING.md`. One skill per pull request, tested against the
localhost targets, no live targets in tests.

## License

MIT. See `LICENSE`.
