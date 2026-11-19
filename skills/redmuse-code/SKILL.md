# RedMuse code review

You review source code white-box for a redmuse run. You reason about
data flow and authorization before you flag anything. A suspicious
pattern with no reachable path is a note, not a finding. A finding
without a live proof in a sandbox or local run is unvalidated.

## Pass order

- Data flow first: trace user input from entry points (routes, handlers,
  CLI args, queue consumers) to sinks (queries, shell, HTML, file paths,
  redirects, deserialization). Flag only flows that actually connect.
- Authorization model second: who can call what, and where ownership is
  checked. Look for missing checks, checks on the wrong object, and
  checks that happen after the action.
- Secrets third: keys, tokens, and passwords in code, configs, and
  history. A secret in code is a finding only if it is live or
  reachable. Mask every secret in your output.
- Dependencies fourth: known vulnerable versions, pinned or not, and
  whether the vulnerable code path is actually reachable.
- Config fifth: debug flags, permissive CORS, weak cookies, missing
  security headers, and dangerous defaults.

## Classes to cover

Injection (SQL, NoSQL, command, XSS through unsafe rendering), broken
access control and IDOR, insecure deserialization, SSRF through URL
handling, path traversal, weak crypto, auth and session flaws, business
logic gaps, and sensitive data exposure.

## Standing probes and review checklist

These items come from repeated misses in fix and review rounds. Apply
them on every code review, not only when a finding names the shape.
For fixed keyword lists in a scanner, see the fixed-list scanner
review in redmuse-cve-intel.

### Overlapping checks

When two checks overlap, cross-reference them in a comment or share a
helper. An undocumented overlap is easy to break by "simplifying" one
of the two checks. Example pattern: a branch that duplicates a
period-2 check for a constant sub-case but also covers non-periodic
cases. Record which cases each check owns and which cases both cover.

### Enumerate every consumer of a shared helper return

Standing probe: enumerate every consumer of `dbRun`/`dbTransaction`
`changes` (and of any shared helper return value with a sentinel) and
tabulate which consumers have a `-1` branch. Any future route that
reads `changes` falls into the same trap, so re-run the enumeration
instead of re-deriving it. The table lists consumer, whether it reads
`changes`, whether it has a `-1` branch, and the verification strength
of that branch (see below).

### Redundancy needs a "can this layer express it" check

When a check looks redundant with a config or routing layer, trace
what information that layer can actually convey to the code before
calling the check dead. A matcher can gate whether a handler runs but
carry no per-entry signal into the handler, so it cannot select
between two variants inside the handler. Surface similarity (both
mention the same path) is not redundancy.

### Enumerated-shape matchers need adversarial variants

A matcher built from enumerated shapes should be reviewed with
adversarial variants of each shape, not just the one reported
example: prefix, suffix, shift, longer, reversed, and flipped forms.
Each round finds a new shape the previous enumeration missed, so test
the variants per shape and record which were tried.

### Lossy normalizers hide the signal

Any check that runs after a lossy normalization should be re-run on
the raw form, or the normalizer should have a less lossy variant (for
example a symbol-only edge strip instead of a strip that also eats
digits). A normalizer that eats a leading digit can both create a hole
and hide a doubled form. When reviewing a normalizer, list what it
discards and ask which check depends on the discarded part.

### Comment and code drift

Cross-check a function's comment against its actual conditions. A
comment that says "block columns move in one direction" while the code
allows a zero step and flips is drift, and a verifier that compares
the comment's claims with the code's conditions catches it without a
live probe. Flag any comment claim the code does not enforce, and any
code condition the comment does not mention, as drift to fix in the
same change.

### Heuristic bounds need adversarial tests

Every bound in a heuristic needs a test at the boundary and just past
it. A proximity check that assumes bridges sit near the runs they join
breaks silently on shifted or long variants. For each bound, record
the boundary value, the at-boundary case, and the just-past-boundary
case.

### Discarded affected-row counts

Flag `delete*` helpers (and any cleanup helper) whose void return
discards `dbRun`'s `{ changes }` when callers log success
unconditionally. A "cleanup succeeded" log is unverifiable when the
affected-row count was thrown away. The fix is to return the count (or
a confirmed/not-found result) and log only on confirmation.

### Changes-based branches state their verification strength

Every `changes`-based branch added in the current PR must state its
verification strength in its comment: attributive (the branch can
tie the change to this caller, for example via an owner id or a key
hash) or state-only (the branch can only say a row changed, with a
documented phantom-success gap where it cannot). This applies to
branches added in the current PR only, not to pre-existing branches
already in the codebase: a worker reviewing an existing codebase
does not have to add strength statements to every old branch, and
only flags an old branch when the change under review touches it.
Require the statement at review time; a branch added in the current
PR with no strength statement is incomplete.

### Route auth needs a single source of truth

Route authorization described in prose in two places drifts with no
single source of truth. Suggest a small table in the README (or a test
that greps the routes and asserts the count) so the next auth change
cannot silently stale the comment. When reviewing auth, check the
table or test first, then the routes.

### When a live result contradicts the code reading, instrument

Do not reason from the diff alone when a live result contradicts the
code reading. Instrument a throwaway copy with internals exported and
re-run the probe against it. The instrumented run, not a re-reading,
decides which reading was wrong.

### Dead caps and bounds

A cap or bound is dead code in practice when another check catches
every input that would reach it. Example pattern: a bridge cap that
never fires because any bridge long enough to hit it is already a
sequential run caught elsewhere. Flag dead caps as a finding class,
and either drop the cap or record why it stays.

### Indexing check caveat

Caveat, not a new rule: a "no `!` indexing" check flags
construction-safe coupling as false positives unless it models the
unmapped-guard first. A function that indexes with `!` only after a
guard that proves the key is mapped is safe by construction. Do not
add a blanket no-`!` rule; any indexing check must model the guard
before flagging.

### Dead-variable lint

Flag variables that are assigned but never read except in their own
null check. An assigned-but-never-read variable is either dead code or
a missing use, and either way it should not survive review.

## Output

Return one record per issue, in the orchestrator shape, plus a reachability
note: the exact flow from entry to sink, or why the flow does not
connect. For every confirmed-by-code issue, state what live proof would
confirm it (local run, sandbox request, or test account call). The
orchestrator or an exploit team runs that proof. Until then, the issue
stays unvalidated in the report.
