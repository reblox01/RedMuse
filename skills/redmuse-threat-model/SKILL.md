# RedMuse threat model

You model a system before anyone scans it, so the scan tests
the right things. A scan without a threat model tests what the
scanner knows, a scan with one tests what the system actually
trusts. This skill runs first, before recon, and its output is
the plan the other teams work from. If the model is wrong, the
scan is wrong, so you write the model down and let the owner
correct it before a probe runs.

## What you need, before you start

- The data flow: what data enters the system, where it is
  stored, where it leaves, and who can see it at each step.
  Draw it as a simple diagram, boxes and arrows, not a work
  of art. A missing arrow is a missing trust boundary.
- The trust boundaries: where data crosses from one trust
  level to another, for example browser to server, server to
  database, server to a third party, staff to admin. Every
  boundary is a place to test.
- The assets: what is worth protecting, in the owner's words,
  not yours. Money, personal data, accounts, parcels, prices,
  admin settings, in that order for a client site.
- The actors: who uses the system, and what each actor is
  allowed to do. A customer, a courier, a seller, an admin.
  An actor that can do something they should not is a
  finding waiting to happen.

If any of those four is missing, you say so, and you model
what you have, with the gaps listed. A partial model is
better than no model, and a guessed model is worse than a
partial one.

## STRIDE, per boundary

For each trust boundary, ask the six STRIDE questions, in
plain words, and write one threat per answer that is not
obviously impossible:

- Spoofing: can someone pretend to be another actor here.
- Tampering: can someone change data in transit or at rest here.
- Repudiation: can someone do something here and leave no trace.
- Information disclosure: can someone read data here they should not.
- Denial of service: can someone stop this step working for others.
- Elevation of privilege: can someone gain a higher role here.

A threat with no boundary attached is a guess. Attach every
threat to the boundary where it happens, and to the asset it
touches.

## DREAD, to rank the threats

Rank each threat with DREAD, one line per letter, and say
which letter you guessed:

- Damage: what breaks if this happens.
- Reproducibility: how easy it is to do again.
- Exploitability: how much skill it needs.
- Affected users: how many people it touches.
- Discoverability: how easy it is to find.

A threat that is easy to find, easy to do, and touches every
user goes to the top of the scan plan, even if the damage
looks small. A threat that needs an insider and touches one
account goes to the bottom, even if the damage looks big.

## Attack trees, for the top threats only

For the top three threats, draw an attack tree: the goal at
the top, the steps to reach it below, with AND and OR between
steps. A step that needs two things at once is AND, a step
with two ways in is OR. The tree shows the scan what to test
first: the cheapest branch, and the branch with the fewest
steps. Do not draw trees for every threat, only for the ones
that decide the scan.

## Output

Return a threat model: the data flow diagram, the trust
boundaries, the assets and actors, the STRIDE threats per
boundary with DREAD ranks, the attack trees for the top
three threats, and the scan plan, which teams test which
boundaries, in what order. List assumptions and gaps
separately, so the owner can correct them before the scan
starts. A threat model nobody read is not a plan, it is a
document, so the scan plan is the part that matters most.
