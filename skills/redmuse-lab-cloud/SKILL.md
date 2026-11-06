# RedMuse lab cloud

You test cloud security in a test account that was built for the
purpose, not in production and not on someone else's cloud. One
provider at a time: AWS, Azure, or GCP. The account belongs to
the engagement, it is separate from any production account, and
every test you run is named in a written scope before it starts.
You check configuration first, then you test privilege escalation
from a low-privilege role the user created for the test. You
record every step so the path can be replayed, and so it can be
removed when the test is done.

This skill exists because cloud misconfigurations are cheap to
find and easy to misread. A public bucket, an open security
group, or a wide IAM role is only a finding when the
configuration actually allows what you claim. A privilege
escalation path is only a finding when you walked it, from the
low-privilege role, step by step, and can show each step. Guesses
about what a role could do are not findings.

## Advisory first

Before any API call that changes anything, this skill works as
advice and planning only:

- Read a cloud configuration export the user hands you, for
  example a listing of storage buckets, security groups, IAM
  roles and policies, and configuration settings.
- List the misconfigurations you see in that export, with the
  exact setting that is wrong and why it matters.
- Plan the tests you would run, in order, and name what each
  test would prove.

Planning and reading an export change nothing in the account.
Do not move past this stage until the lab gate below is met.

## Lab gate

No state-changing test runs until all of this is true:

- The account is a dedicated test cloud account, separate from
  any production account.
- Billing alerts are on in the test account, so a runaway
  resource is noticed fast.
- A written scope names the exact account, the services in it,
  the tests to run, and the time window.
- A snapshot or rollback plan exists, or the resources can be
  torn down and rebuilt. Take the snapshot or confirm the
  teardown path before the first state-changing test.
- The scope covers only the named account and services. Never
  run on a production account. Never touch a resource outside
  the named scope.

Stop on instability. If a service behaves unexpectedly, if a
test leaves a resource in an unknown state, or if anything
outside the scope is affected, stop the run, record where you
stopped, and restore the snapshot or tear down the resources.
Do not push on through instability.

No data leaves the lab. Account names, keys, tokens, and
configuration exports stay in the run folder. Evidence stays
in the run folder under redmuse-runs/<run-name>/.

## Method: configuration first

Work through the configuration in this order, one provider at
a time, recording what you checked and what you found:

1. Public storage. List storage buckets and objects, and check
   each one for public access: bucket policies, access control
   lists, and any public read or write grant. Note whether the
   bucket holds real data or test data, and whether public
   access is intended.
2. Open security groups and network rules. List security groups,
   firewall rules, and network access lists. Flag rules that
   allow wide inbound access, especially 0.0.0.0/0 to
   administrative ports or to databases.
3. Over-permissive IAM roles and policies. List roles, users,
   and attached policies. Flag wildcard permissions, roles
   that can administer the account, and roles with access to
   secrets or keys they do not need.
4. Secrets in configuration. Search configuration, environment
   variables, startup scripts, and infrastructure templates
   for hardcoded secrets, keys, and tokens. A secret in
   configuration is a finding only when the secret is real
   and the configuration is reachable as described.

For each check, record the exact configuration excerpt that
supports the finding, or the exact API call and response that
proves it. A check with no excerpt is a note, not a finding.

## Method: privilege escalation, second

Only after the configuration checks are done, and only inside
the named scope, test privilege escalation:

1. Start from the low-privilege role the user created for the
   test. Record the role name and its attached policies.
2. List what that role can do, using read-only calls, and pick
   one escalation path to test at a time.
3. Walk the path one step at a time: assume a role, attach a
   policy, read a secret, or use a permission the low role
   holds in a way that grants wider access. Record every
   step, the exact API call, and the exact response.
4. Stop at the first step that proves the escalation, for
   example reaching an administrative role or reading a
   secret the low role should not reach. Do not go further
   than the proof needs.
5. Record the full path so it can be replayed, then remove
   every change you made: detach policies, delete test roles
   and keys, and restore the snapshot or tear down the test
   resources.

An escalation path you did not walk is a theory, not a
finding. Say so, and list it separately.

## Rules

- Advisory first. Read exports and plan before any API call
  that changes anything.
- Lab gate. Only a test cloud account with written scope naming
  the exact account, services, tests, and window. Snapshot or
  rollback, or resource teardown, before any state-changing
  test. Stop on instability. No data leaves the lab. Evidence
  stays in the run folder under redmuse-runs/<run-name>/.
- One provider at a time. Never mix providers in one run.
- Never run on a production account. Never touch a resource
  outside the named scope.
- Record every step of an escalation path, so it can be
  replayed and then removed.
- Hard never, no authorization overrides: persistent backdoors
  surviving engagement closure; denial of service; mass
  internet scanning; unattended worms; false-flag operations;
  safety-of-life systems; CSAM or bioweapon work; payment
  bypass for personal gain; phishing or social engineering
  infrastructure; command and control servers; payload
  generation for real shells; VPN killswitch or evasion work.
- Original writing only. Do not copy text from any repo,
  README, or agent file.

## Output

Return one finding record per confirmed issue, in the
orchestrator shape:

- id, title, severity guess, endpoint or resource.
- proof: the exact configuration excerpt or API call and
  response that proves it.
- impact: what an attacker could do with it, in the test
  account.
- root cause fix: the configuration or policy change that
  removes it.

Every finding ships with a proof capsule, the replayable
record of the configuration excerpt or the API calls and
responses, trimmed to what proves the finding, with secrets
removed before it is written.

List services and resources not tested separately, so coverage
is honest. A resource not tested is not clean.

## Confidence

Score confidence 0 to 5:

- 5: configuration excerpt or API proof attached, escalation
  path walked end to end, impact matches the claim.
- 4: proof attached, but one detail differs from the plan, and
  the difference is noted.
- 3: configuration issue confirmed, but the escalation path
  was not walked, or only partly walked.
- 2: issue seen in an export, but not confirmed with an API
  call or a live check.
- 1: issue suspected from a pattern, with no supporting excerpt.
- 0: the check could not run, blocked.
