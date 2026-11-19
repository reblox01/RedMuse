# RedMuse CI gate

You add redmuse scanning to CI/CD so every pull request gets a
diff-scoped security gate. The gate blocks merges on real findings and
never blocks on noise. GitHub Actions is the reference pipeline. Other
pipelines follow the same shape.

## Gate design

- Trigger: pull requests and pushes to the default branch.
- Scope: diff mode only. The run tests what changed, not the whole
  codebase, so it stays fast enough for a merge gate.
- Steps: check out the PR, install the redmuse skills, run the
  orchestrator in diff mode against the changed code and a staging
  target when one exists, and write findings.json as an artifact.
- Verdict: fail the build when any confirmed finding is high or
  critical. Medium and low findings comment on the PR but do not fail
  it. Unvalidated findings never fail a build.
- Output: a PR comment with the severity counts and the top findings,
  plus the full report as a downloadable artifact.

## Workflow sketch

```yaml
name: redmuse gate
on:
  pull_request:
  push:
    branches: [main]
jobs:
  redmuse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install redmuse skills
        run: |
          # Copy skills/ from the redmuse repo into the runner's
          # skill folder, or vendor the pack in this repo. The
          # destination below is an example: adapt it to the
          # runner's actual skill folder.
          cp -r skills/ "$HOME/.muse/skills/redmuse/"
      - name: Run diff scan
        run: |
          # Reference invocation pattern, pseudocode: no Muse
          # runner command ships in this repo yet, so the exact
          # command depends on the runner. The contract is: run
          # the orchestrator in diff mode against the PR diff,
          # and write findings.json for the verdict step below.
          muse run redmuse-orchestrator --mode=diff --diff="$(git diff origin/main)" --output redmuse-runs/ci/
      - name: Fail on confirmed high or critical
        run: |
          # Concrete exit-code check. Exit 1 fails the build when
          # any finding in findings.json is high or critical with
          # a verified or confirmed status. Unvalidated, candidate,
          # and open findings never fail a build. Exit 0 passes.
          # If the runner writes a different status word for a
          # confirmed finding, adapt the status match to its
          # schema, and never widen it to unvalidated findings.
          python3 - <<'EOF'
          import json, sys
          with open("redmuse-runs/ci/findings.json") as fh:
              data = json.load(fh)
          blocking = [
              f for f in data.get("findings", [])
              if f.get("severity") in ("high", "critical")
              and f.get("status") in ("verified", "confirmed")
          ]
          if blocking:
              print("blocking findings:")
              for f in blocking:
                  print(" ", f.get("severity"), f.get("id"))
              sys.exit(1)
          print("no confirmed high or critical findings, gate passes")
          EOF
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: redmuse-report
          path: redmuse-runs/
```

Adapt the install and scan steps to the runner's Muse setup. The shape
above is the contract: diff scope, severity verdict, comment, artifact.

Status: this workflow is a reference, not a runnable gate yet. No
Muse runner command ships in this repo, so the `muse run` line above
is a pseudocode pattern, not a tested command. It becomes runnable
only when a working runner exists, the verdict step reads a real
machine-readable findings.json, and a failing integration test
proves the gate fails on a PR with a known confirmed high finding.
Until then, do not claim the gate is live. A nonzero exit from the
scan step itself means the scan errored, which is different from a
finding blocking the merge; keep the two apart in the run log.

## Rules

- The gate runs on the PR diff, never on the whole repo, unless the
  team explicitly asks for a full run.
- Secrets in CI logs are masked. A finding that includes a secret is
  reported with the secret masked.
- A failing gate links to the per-finding files, so the author can fix
  without asking what failed.
- Flaky gates lose trust fast. If a check fails without a reproduced
  proof, treat it as a gate bug and fix the gate before blaming code.
- For the real Strix engine in CI instead of redmuse, use the
  ci-security-scanning-with-strix skill. Same gate shape, different
  engine. Say which engine the pipeline uses.
