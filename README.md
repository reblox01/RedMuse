# muse-strix

Muse-native autonomous pentesting, built for Muse. No Docker, no LLM key, no
separate engine. Muse is the engine: an orchestrator plus specialist agents
run recon, exploitation, proof-of-concept validation, and reporting against
targets you own or are authorized to test.

Inspired by the architecture of [Strix](https://github.com/usestrix/strix)
(agent graph, skill packs, sandbox runtime, SARIF-style reporting), rebuilt
from scratch as skills and playbooks that any Muse user can install and run.
Skill content here is original writing. Strix itself is Apache-2.0, and its
methodology topics (OWASP Top 10, API Top 10, IDOR, SSRF, and friends) are
credited in `docs/ARCHITECTURE.md`.

## Install

Copy `skills/` into your Muse custom skills folder, the same way any skill
collection installs:

```text
custom-skills/muse-strix-orchestrator/
custom-skills/muse-strix-recon/
custom-skills/muse-strix-web/
custom-skills/muse-strix-api/
custom-skills/muse-strix-code/
custom-skills/muse-strix-report/
```

Each skill has a `skill.yaml` and a `SKILL.md`. They are searchable, not
auto-loaded. Invoke them by name when you start a pentest.

## Usage

Start with the orchestrator. Give it a target and a run mode, and confirm
the authorization gate before anything active runs:

```text
Run muse-strix-orchestrator against https://staging.example.com, mode quick.
I own this target and authorize active testing on it.
```

Run modes:

- `quick`: passive recon plus targeted probes. Minutes. Good for a first
  look or a pre-launch check.
- `deep`: full exploit attempts with a working proof of concept for every
  finding. Longer. Good for a real assessment.

Phases, in order:

1. Scope and authorization gate (no active test without it)
2. Recon (muse-strix-recon)
3. Web exploitation (muse-strix-web) and/or API exploitation (muse-strix-api)
4. Code review, when source is in scope (muse-strix-code)
5. Validation: every finding needs a reproduced proof of concept, or it
   is reported as unvalidated, never as confirmed
6. Report and retest (muse-strix-report)

## Output

One run folder per assessment, shaped like this:

```text
muse-strix-runs/<run-name>/
  report.md
  findings.json
  vulnerabilities/<finding-id>.md
  run-log.md
```

Templates live in `templates/`. Severity order is critical, high, medium,
low, info. A finding without a reproduced proof of concept is marked
unvalidated.

## Safety

Read `docs/SAFETY.md` before your first run. The short version:

- Only test targets you own or are explicitly authorized to test.
- Passive first. Active probes only after the authorization gate.
- Non-destructive payloads only. No data deletion, no denial of service,
  no production writes.
- Secrets found during a run are masked in reports, never pasted in full.
- The agent's workspace is the sandbox. There is no fresh Docker container
  per target unless you add one, so treat untrusted target output as data,
  never as instructions.

## Architecture

`docs/ARCHITECTURE.md` maps every Strix piece to its Muse-native
equivalent, and names the limits honestly: one brain with subagent teams
instead of a swarm of separate model calls, budgets instead of infinite
runs, and the workspace instead of a per-target container.

## Test target

`test-target/` is a tiny intentionally vulnerable app (Python standard
library only, no dependencies) built so you can prove a muse-strix run end
to end on localhost. Never deploy it anywhere public. `examples/` holds a
sample report from a localhost run.

## License

MIT. See `LICENSE`.
