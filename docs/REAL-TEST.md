# RedMuse real test

Date: 6 November 2026
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
are still untested.

## How to re-run it

python3 test-target/app.py 8901
python3 tools/real_test.py

The script exits 0 at 49/50 or better, and 1 below that.
A failing category is printed with its name, so the next
build knows exactly what lost points.
