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
          # skill folder, or vendor the pack in this repo.
          echo "install step goes here"
      - name: Run diff scan
        run: |
          # Invoke the orchestrator in diff mode against the PR diff.
          # Fail on confirmed high or critical findings only.
          echo "scan step goes here"
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: redmuse-report
          path: redmuse-runs/
```

Adapt the install and scan steps to the runner's Muse setup. The shape
above is the contract: diff scope, severity verdict, comment, artifact.

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
