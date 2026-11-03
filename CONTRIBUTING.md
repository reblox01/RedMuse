# Contributing

redmuse is built for Muse users, by Muse users. Contributions are
welcome, with one rule above all: nothing in this repo may encourage
testing a target without authorization.

## How to contribute

- Fork, branch, commit per step, open a pull request.
- One skill per pull request, or one feature per pull request. Small
  and reviewable beats big and vague.
- New skills follow the pack format: a folder `skills/<name>/` with
  `skill.yaml` (name, title, description, category, include_in_prompt)
  and `SKILL.md` (instructions only, no frontmatter).
- Skill text must be original writing. Methodology topics (OWASP,
  standard vuln classes) are fine to cover. Copying another project's
  skill text is not.
- Every new vuln class or mode needs a planted flaw in a localhost
  test target plus a sample report that proves it, the same way the
  web and API targets prove the current pack.

## Tests

There is no test suite with assertions yet. The proof standard is a
live run: start a test target on localhost, run the orchestrator in
quick mode, and show the sample report. A pull request without a
reproduced proof is a draft, not a merge candidate.

## Rules

- Never add a live target, a real credential, or a real user record to
  the repo, in code, tests, or examples.
- Never add a destructive payload. Proofs use harmless markers only.
- Keep the safety gate intact. A change that weakens the authorization
  gate is a rejection, not a discussion.
- Keep it Muse-native. A feature that needs Docker or a paid key
  belongs behind an optional note, not as a requirement.
