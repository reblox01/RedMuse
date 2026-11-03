# Update check sample report

Run: tools/check_updates.py, from the RedMuse repo, before a run.
Date: 3 Nov 2026. This run uses the expanded config: 13 sources
in skills/redmuse-update/sources.yaml, up from 9. No script edit
was needed to add the 4 new sources; adding them to the YAML was
enough, which is the point of the config.

## Raw output

```text
redmuse | c608756f874ec89212a8b5c7bd1a442a62678044 | c608756f874ec89212a8b5c7bd1a442a62678044 | up-to-date
strix | reference-only | 6b7ae2ebe4d47037a927aade23265ff4e4f27e84 | manual-review-if-changed
securly | reference-only | 73060652979917c4548533272f67fe78a5a5e47c | manual-review-if-changed
cloudflare | reference-only | c1c8a8c1471069fb0e188eeaff69b8e8db6564a8 | manual-review-if-changed
sentry | reference-only | 0c464f411bdfb8d4c12314b36264d06cb2f60270 | manual-review-if-changed
owasp | reference-only | 8ac7965caa212b4a850aff8d3df0081ab3fa9eed | manual-review-if-changed
masriyan | reference-only | 3aa77d84fb64cf07b550f6be4544bb91292db89f | manual-review-if-changed
trailofbits | reference-only | 711af095215ad4ecde5b90cd1d0124b3f1c4ca9e | manual-review-if-changed
openai | reference-only | 1503a508778dad94e9469e202ee941b04004734f | manual-review-if-changed
clawsec | reference-only | e46beec4f559e15c57d250023298391253e9ce43 | manual-review-if-changed
varlock | reference-only | db875a056a8422295b53e86f4b70fc2ec99bdc16 | manual-review-if-changed
rea | reference-only | 8c857ce56c68ca46d202db0c9571277974c9e167 | manual-review-if-changed
squirrelscan | reference-only | d1f585cdc299d5f55582b8e4d5e393ad43e5a783 | manual-review-if-changed
```

## Reading the result

- RedMuse: up-to-date. Local HEAD matches origin/main, so no pull
  is needed. The config maps all 11 RedMuse skills to this one
  repo through the covers list.
- Strix, Securly, Cloudflare, Sentry, OWASP, Masriyan, Trail of
  Bits, OpenAI: unchanged reference values from the previous
  sample run.
- ClawSec, Varlock, REA, SquirrelScan: new reference sources,
  each verified against its repo before being added. ClawSec is
  an agent-side integrity layer, not a probe skill, and its
  auto-restore behavior stays opt-in. Varlock covers secret
  handling. REA covers binary targets only, authorized scope
  only. SquirrelScan audit-website covers web audits plus an
  iterative fix loop. Picks and scope notes are recorded in
  docs/SOURCES.md, including the skills considered and not
  added, with reasons.
- Azure Key Vault was not added: its directory page names no
  git repo, it needs the mcp_microsoftdocs MCP for live docs,
  and it is Azure-only.
- CLI note: the sources name CLIs (semgrep, codeql, nmap,
  nuclei, trivy, ZAP, sqlmap, tshark, Suricata, Snort, Zeek,
  varlock, squirrel, rea-agents, clawsec). None of them are
  installed on the demo VM, so those paths are dormant there.
  Availability is checked on the run machine, never claimed
  without that check.

## Follow-up tasks opened

None. No methodology delta was assessed in this check run.
