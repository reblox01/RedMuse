# RedMuse real test

Date: 19 November 2026 (revised; first version 6 November 2026)
Tool: tools/real_test.py, standard library only.
Target: test-target/app.py on http://127.0.0.1:8901, fake data
only, localhost only. The target has 4 planted flaws: IDOR on
/user?id=, API BOLA on /api/users/, reflected XSS on /search?q=,
and open redirect on /redirect?url=.

## Result

50/50 = 10.0/10, on this target, on this run.

- find, 10/10: all 4 planted flaws found with their exact proof.
- verify, 10/10: every finding re-run unchanged and reproduced,
  plus a false claim (id=999 returns a user) correctly rejected
  with a 404.
- chain, 10/10: IDOR web plus BOLA api, same admin record from
  two surfaces, and reflected XSS plus open redirect, the
  phishing link story, both proven end to end.
- risk, 10/10: every verified finding has a CVSS 3.1 vector
  and a priority rank.
- store, 10/10: all 4 verified findings in the findings store
  with the right status and confidence 5.

## Honest basis, revised 19 November 2026

The earlier 50/50 was weaker than presented: three checks were
hardcoded True (the no-missed-flaw check, the verify-verdicts
check, and the store-stats check), the risk vectors were written
in by hand, and the chain tests issued independent requests.
The 19 November version removes every free point, and the score
is earned live in the run:

- find: the no-missed-flaw check counts the flaws found by the
  live probes in this run. It passes only at 4/4.
- verify: the verdicts check reads back the verification record
  this run wrote (/tmp/redmuse-real-test-verify.json) and asserts
  all 5 entries reproduced: the 4 findings plus the false claim.
  The static example file is not used. This revision also adds
  the missing open-redirect re-run: the earlier verify section
  re-ran only IDOR, BOLA and XSS, so only 3 of the 4 findings
  were ever verified. Verify points are rebalanced to keep the
  section at 10 with the added re-run.
- chain: each chain passes a value returned by the first link
  into the second. The BOLA response returns the user id, and
  that id is used in the web IDOR request; the search page
  reflects a crafted URL, and that reflected URL is used as the
  open-redirect target.
- risk: each CVSS 3.1 vector is computed in the run from the
  verified finding and its live evidence (unauthenticated
  request, victim interaction needed or not, scope change or
  not), written to a risk record this run
  (/tmp/redmuse-real-test-risk.json), and each check reads that
  record back. Ranks are computed from severity, not written
  in per finding: rank 1 plus the count of verified findings
  with a strictly higher severity.
- store: findings are stored with the real findings CLI, the
  count is read from the database, and the stats check runs the
  real stats command (tools/findings.py stats) and asserts its
  output says total 4 and verified 4.

An intermediate run of the revised script scored 35.5/50 and
failed exactly the checks the old version gave away for free,
which shows the new checks bite: the verdicts, risk and store
checks fail when a finding is not verified in the run.

## What this score does and does not mean

This is a real test, not a rating from a list of skills. The
probes ran, the responses came back, and the score is the
count of checks that passed. It is not a claim that RedMuse
scores 10/10 on every target. The test target is small and
its flaws are known, so a 10 here means the pipeline works
end to end: find, verify, chain, risk, store. It does not
mean a live complex app would score the same, and it does
not mean the lab tier is done. The lab skills are being built
separately, and live authenticated chains on a complex app
are still untested. It also does not prove the CVSS vectors
are the only correct ones: they are computed from the live
evidence on this small target, and a reviewer may disagree
with a metric on a real target.

## How to re-run it

python3 test-target/app.py 8901
python3 tools/real_test.py

The script exits 0 at 49/50 or better, and 1 below that.
A failing category is printed with its name, so the next
build knows exactly what lost points.
