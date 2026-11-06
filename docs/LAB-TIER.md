# RedMuse lab tier

Date: 6 November 2026
Status: design only. No lab skill exists yet. This doc decides what the
lab tier is, what belongs in it, and what never belongs in it, so the
skills can be built one at a time without drifting into a different
project.

## What the lab tier is

The lab tier is a separate, clearly labelled Tier 2 pack inside
RedMuse. Core RedMuse stays exactly what it is: Muse-native, no
Docker, no LLM key, no tool install, and it runs in a plain
Muse.ai session. The lab tier does not change that. It is an
opt-in extension for work the core can never do, because the
work needs a machine, a network, or a tool stack that a
browser session does not have.

A lab skill needs a Kali box or a Docker host on a machine the
user controls. It never runs in a plain Muse.ai session. It never
runs on a live client site. It runs only in three places: on
localhost, on a local lab VM the user owns, or on a target with
written scope that names the exact asset, the exact tests, and
the exact window. If none of those three is true, the skill does
not run, and the run records it as not run.

The lab tier is how RedMuse gets stronger without breaking its
promise. The core finds and proves web, API, auth, code, and UI
holes with harmless markers. The lab tier adds the rest of a
pentest: networks, containers, binaries, mobile apps, cloud
accounts, and the evidence that comes out of them. The two
tiers share one gate style, one finding record, one verifier,
and one report. They do not share one runtime.

## Why two tiers, not one bigger pack

Merging the lab into the core would kill the core. The moment a
skill needs Kali, Docker, or an installed scanner, the pack
stops working in Muse.ai, and the user who only wants a web
audit has to set up a lab first. That is the exact trade the
other tools made, and it is why none of them runs where RedMuse
runs. Keeping the tiers separate lets a user run the core with
nothing installed, and add the lab only when the target needs
it and the machine is ready.

The split also keeps the risk in the right place. Core skills
are safe to run against a staging site because their proofs are
harmless markers and their worst case is a failed request. Lab
skills touch networks, kernels, containers, and binaries, and
their worst case is a crashed VM or a corrupted disk. That work
belongs behind a snapshot, on a machine that can be rolled back,
not in the same session as a client report.

## The lab gate, stricter than the core gate

The core gate asks for target, scope, mode, budgets, and the
user's explicit confirmation in their own words. The lab gate
asks for all of that, plus six more things, and it stops if any
one of them is missing.

1. Written scope. The target is named as a lab asset, not as a
   domain or a company. The scope lists the exact hosts, VMs,
   containers, binaries, apps, or cloud accounts, and the exact
   tests allowed on each. A lab asset that is not listed is out
   of scope, even if it sits on the same network.
2. Lab inventory. Before any test, the run log records what the
   lab is: the host machine, the VM or container, the tool
   versions that matter, and the network the lab sits on. A
   test that cannot say where it ran is not a test.
3. Snapshot and rollback. Before any test that changes state,
   take a snapshot of the VM or container, or copy the binary,
   image, or capture file being worked on. The rollback step is
   written down before the test starts, not invented after
   something breaks. If there is no snapshot and no rollback,
   the test does not run.
4. Stop on instability. On any sign of target instability, a
   service that stops responding, a VM that slows or freezes,
   a container that restarts on its own, stop active tests at
   once, roll back, and note it in the run log. Do not push
   through instability to get one more finding.
5. No data leaves the lab. Captures, disk images, memory dumps,
   binaries, and credentials found in the lab stay in the run
   folder on the lab host. They are not uploaded, pasted into
   chat, or sent to a third-party service. A finding is reported
   as a description and a redacted proof capsule, never as the
   raw material it came from.
6. Evidence stays in the run folder. Every lab test writes its
   commands, its output, and its proof capsule under
   redmuse-runs/<run-name>/, next to the core findings. Raw
   output is kept only for confirmed findings, same as the
   core. When the run ends, the lab is rolled back to its
   snapshot, and the run folder is the only thing that remains.

A lab run that skipped any of these six says so in its report,
and the classes it skipped are listed as not run, never as clean.

## Tool guardrails, from NmapMCP

Every tool a lab skill calls, and every MCP a lab run uses, follows
these five rules. They are the guardrail pattern of the NmapMCP
server, written here as the rule for any lab tool, not as a quote
of that project:

1. Flag allowlist. Only the flags the skill lists for that tool
   may reach the shell. An agent never invents a new flag, and a
   flag outside the list is refused, not tried.
2. Private-range guard. Lab tools run against lab addresses only.
   A public address is refused unless the written scope names it
   explicitly. A range the scope does not name is out, even if
   it sits on the same network.
3. Concurrency cap. At most 3 scans or heavy tool runs in
   parallel. A fourth waits. This keeps one agent from
   flooding its own lab.
4. Hard timeout. Every tool call has a fixed maximum run time,
   written in the skill. A call that hits it is killed, its
   partial output is kept, and the run moves on. No call runs
   without a timeout.
5. Output diffing. Results are saved per run, so a later run can
   diff against the earlier one. The diff is how a fix is proven:
   what changed, what stayed, what is new. A finding without a
   saved result to diff against is unvalidated.

A tool that cannot meet all five does not run in the lab. A
generic run-any-command tool fails rule 1 by design, so it is
never used as a lab tool, however convenient it looks.

## The skills, in build order

Every lab skill is built advisory-first. That means the first
version of the skill must be usable as advice before it is
usable as execution: it can read a config, a capture, or a
binary, explain what is wrong, and say what to test next, with
no tool running and no target touched. Execution is added only
after the advisory version works, and only behind the lab gate.
A skill that cannot advise is not ready to execute.

Build order is by how close each skill is to what Sohail is
already learning, and by how little hardware it needs. The
first skills need only files and a VM. The later skills need
devices, cloud accounts, and a blue-team setup.

### 1. redmuse-lab-traffic, traffic analyzer

What it tests: captured network traffic, offline, after the
fact. It reads a pcap file the user provides, dissects the
conversations in it, and looks for what should not be on the
wire: credentials in clear text, sessions without TLS, DNS
queries that leak internal names, and protocols that should
have been encrypted. It reconstructs the story of a capture
in order, so a finding can say what happened, when, and between
which hosts, instead of quoting a single packet.

What it needs: a pcap file, and a lab host that can read it.
No live sniffing, no interface in promiscuous mode, no capture
on a network the user does not own. Advisory first: it can
explain a capture and point at the interesting flows before
it ever runs a tool. This is first because it matches the
cyber plan directly: Wireshark on one capture is already a
week-one task, and this skill turns that habit into a RedMuse
finding.

### 2. redmuse-lab-network, network attacker

What it tests: a lab network at layer 2 and layer 3. Host
discovery, port and service enumeration, and the classic local
network weaknesses: name resolution poisoning, ARP spoofing,
and services that answer without authentication. It maps the
lab network the way recon maps a website, then tests the
services it found, one at a time, with the same harmless-marker
discipline as the core: prove the service answers, do not break
it, do not take it over.

What it needs: a lab network the user controls, with at least
two VMs on it, and a Kali box or a scanner on the same network.
It never runs on a production network, a shared office network,
or a public range. Advisory first: it can read a network diagram
and a scan result and say where the weak points are, before it
ever sends a packet.

### 3. redmuse-lab-container, container breakout in lab

What it tests: Docker and Kubernetes workloads the user runs
in the lab. It checks container configuration first: privileged
containers, host mounts, exposed Docker sockets, and capabilities
that should not have been granted. Then it tests escape paths
from inside a lab container, in a container that was built to
be escaped, with a snapshot taken first.

What it needs: a local Docker host or a lab Kubernetes cluster,
and a deliberately vulnerable container image. It never runs
against a production cluster or a container that holds real
data. Advisory first: it can audit a Dockerfile and a compose
file and list the risky settings, with no container running.
This is third because RedMuse itself deliberately has no Docker,
so the lab tier is the only place container work belongs.

### 4. redmuse-lab-privesc, privilege escalation in lab

What it tests: local privilege escalation on a lab VM, after a
foothold that was already granted in the lab. It enumerates the
machine the way an attacker would: SUID binaries, writable
system paths, scheduled tasks, service permissions, and kernel
versions against CVE intel. It proves one path at a time, with
a snapshot taken first, and it stops at the proof: a command
that shows the higher privilege, not a session that keeps it.

What it needs: a lab VM with a low-privilege account the user
controls, and a snapshot to roll back to. It never runs on a
machine the user does not own, and it never leaves a new account,
a new key, or a changed permission behind. Advisory first: it
can read the output of an enumeration and rank the paths by
likelihood, before anything is executed. This skill exists
because privilege escalation is a real pentest step, and the
lab is the only honest place to learn and prove it.

### 5. redmuse-lab-reverse, reverse engineer

What it tests: a binary, a library, or a firmware image the
user provides. It identifies what the file is, what it links
against, what strings and symbols it carries, and where its
interesting logic lives, then follows one function at a time
to find the flaw: a hardcoded credential, an unsafe parser,
or a check that can be bypassed. It works on a copy, never on
the only copy, and it never runs an unknown binary on a host
that matters.

What it needs: a lab host with a disassembler and a decompiler,
and a target binary the user owns or is authorized to analyze.
Advisory first: it can explain what a binary does and where to
look, before it opens it in a tool. This is fifth because it
needs no network and no target service, only a file and patience,
and it is the deepest cyber skill in the tier.

### 6. redmuse-lab-cloud, cloud security

What it tests: a cloud test account, one provider at a time.
It checks the configuration first: public storage, open security
groups, over-permissive IAM roles, and secrets in configuration.
Then it tests privilege escalation inside the account, from a
low-privilege role the user created for the test, and it records
every step so the path can be replayed and then removed.

What it needs: a dedicated cloud test account, separate from
any production account, with billing alerts on and a written
scope that names the account and the services in it. It never
runs on a production account, and it never touches a resource
outside the named scope. Advisory first: it can read a cloud
configuration export and list the misconfigurations, with no
API calls that change anything.

### 7. redmuse-lab-mobile, mobile pentester

What it tests: an Android or iOS app the user provides, in a
test build. It reads the app package first: permissions, exported
components, hardcoded secrets, and insecure storage. Then it
tests the app's API the way redmuse-api tests a web API, with
the same harmless markers, and it checks what the app stores
on the device and what it sends over the network.

What it needs: an emulator or a test device, a test build of
the app, and a test account. It never runs on a production app
with real user data, and it never touches another user's device.
Advisory first: it can audit an app package and list what to
test, before the app ever runs.

### 8. redmuse-lab-forensics, forensics analyst

What it tests: a disk image, a memory dump, or a network capture
the user provides, after an incident or a lab exercise. It
acquires the evidence properly first, records hashes, and then
works on a copy, never on the original. It reconstructs what
happened: what ran, what changed, what left the machine, and in
what order, so the report can say what is known, what is
inferred, and what is still unknown.

What it needs: an evidence file and a lab host with enough disk
to hold a working copy. It never runs on a live machine that is
still in use, because every command on a live machine changes
the evidence. Advisory first: it can read an existing timeline
and say what is missing, before it opens an image.

### 9. redmuse-lab-malware, malware analyst

What it tests: a sample the user provides, in a sandbox that
has no network route to anything real. It starts static: file
type, hashes, strings, imports, and what the sample claims to
be. Then it runs the sample in the sandbox and records what it
does: files it touches, processes it starts, and network
connections it tries to make, all of which fail because the
sandbox has no route out.

What it needs: an isolated sandbox VM, with snapshots, no
shared folders, and no network except a controlled sink that
logs and drops. It never runs a sample on a host that matters,
and it never uploads a sample to a public service without a
separate decision. Advisory first: it can explain a static
analysis report and say what the sample looks like, before it
ever runs.

### 10. redmuse-lab-detect, detection engineer

What it tests: whether an attack would be seen. It is the blue
team skill in the tier, and it pairs with every offensive skill
above it. For each lab test, it asks what log, rule, or alert
should have fired, checks whether it did, and writes the
detection that was missing. It turns a successful lab attack
into a detection rule, so the same attack fails quietly next
time because it is seen, not because it is blocked by luck.

What it needs: logs from the lab tests, and a place to write
rules, such as a SIEM or a simple log store in the lab. It
never needs a production SIEM, and it never changes a production
rule. Advisory first: it can read a lab attack report and write
the detection that should have caught it, with no logs at all.
It is last because it only makes sense once the other nine
skills are producing attacks to detect.

## Hard never list

No authorization overrides this list. Not the user's, not a
client's, not a written scope, not a lab. If a request asks for
any of these, the answer is no, and the refusal goes in the run
log.

- Persistent backdoors surviving engagement closure. Nothing
  is left behind that keeps access after the run ends. A lab
  VM is rolled back, a test account is deleted, a key is
  revoked.
- Volumetric or protocol denial of service. No floods, no
  amplification, no resource exhaustion, no test that takes a
  service down to prove it can be taken down.
- Mass scanning of the public internet. No internet-wide sweeps,
  no scanning of ranges the user does not own or does not have
  written scope for.
- Unattended worms or self-propagating implants. Nothing that
  spreads on its own, even in a lab.
- False-flag operations. Nothing designed to make an attack
  look like it came from someone else.
- Safety-of-life systems. No SCADA, ICS, medical devices, or
  any system where a failure can hurt a person.
- CSAM or bioweapon content. No creation, handling, or analysis
  of either, for any reason.
- Bypassing payment systems for personal gain. No free purchases,
  no fare evasion, no theft framed as a test.
- Phishing and social engineering infrastructure. No credential
  capture pages, no pretexting campaigns, no vishing, no
  infrastructure built to trick a person.
- Command and control servers. No C2 framework, no beacon, no
  listener waiting for a compromised machine to call home.
- Payload generation for real shells. No msfvenom payloads, no
  reverse-shell one-liners, no shellcode. The core already proves
  holes with harmless markers, and the lab tier proves them the
  same way. A real shell is not a proof, it is a weapon.
- VPN killswitch and evasion. No rotating VPN endpoints to dodge
  a rate limit, no AV or EDR evasion, no hiding from detection.
  A lab test that cannot be seen is a lab test that cannot be
  trusted, and detection is the whole point of the tenth skill.

## How it plugs into the orchestrator

The orchestrator does not change its shape. It gains one
branch, and the core promise stays intact.

- Core skills stay no-setup. A run that uses only core skills
  needs nothing installed, and nothing in the lab tier is
  loaded, offered, or required.
- Lab skills are opt-in. The orchestrator offers the lab tier
  once, at the start, after the core gate. The user says yes
  to a specific lab skill for a specific lab asset, or the
  tier stays off for the whole run.
- Lab availability is checked before lab work starts. The
  pre-run check records whether a lab host exists, whether
  the named VM or container is up, and whether a snapshot
  exists. A lab skill with no lab available is recorded as
  not run, never as clean, and the run continues on the core
  alone.
- Lab findings go through the same pipeline as core findings:
  the same finding record, the same independent verifier in
  redmuse-verify, the same ensemble dedupe, and the same
  report. A lab finding with no proof capsule is unvalidated,
  same as a core finding.
- Lab budgets are separate from core budgets. A lab run gets
  its own probe budget, its own wall time, and its own stop
  conditions, recorded in the run log alongside the core
  numbers. Hitting a lab budget stops lab work only, not the
  core run.
- The run folder is shared. Lab evidence, snapshots notes,
  and proof capsules live under redmuse-runs/<run-name>/,
  next to the core findings, so one report tells the whole
  story and one folder holds the whole proof.

## What it does not do

- It does not turn RedMuse into a Kali replacement. The lab
  tier does not ship a tool stack, does not install Kali, and
  does not bundle scanners. The user brings the lab, RedMuse
  brings the method. A skill that needs a tool says which tool
  and why, and the pre-run check says whether it is there.
- It does not make RedMuse autonomous in the lab. Every lab
  test is gated, every high-risk step is approved, and the
  orchestrator stops on instability. The lab tier is not a
  button that runs a pentest on its own.
- It does not move core work into the lab. Web, API, auth,
  code, and UI audits stay in the core, with no setup. A
  website is never a lab target just because a lab exists.
- It does not lower the bar for proof. Lab findings need the
  same proof capsule as core findings, verified by the same
  independent verifier, or they are unvalidated.

## Decision

Build the lab tier one skill at a time, in the order above,
advisory first, execution second, each behind the lab gate.
Do not build a lab skill because a tool list mentions it.
Build it because a target needs it and a lab exists to run it
in. When the tenth skill is done, RedMuse will cover a whole
engagement: a web audit in Muse with nothing installed, and a
lab pentest on a machine the user controls, with the same gate,
the same proof, and the same report. That is how it beats the
other tools: not by copying their tool stacks, but by being
the one pack that is honest about what it tested, what it did
not test, and what it refused to do.
