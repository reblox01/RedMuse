# Sample verification run: localhost test target

Target: http://127.0.0.1:8901, the RedMuse test target in
test-target/app.py. Fake data only, localhost only, run 6 Nov 2026.
The verifier received only the finding records below, not the
finder's reasoning. Each proof was re-run unchanged, with the
same harmless marker.

## 1. idor-user-profile, verified, confidence 5

Finding record: GET /user?id=2, expected a 403 or a redirect to
the requester's own profile, actual 200 returning Bob Test,
role admin, balance 99999.

Verification, re-run: GET /user?id=2 returned 200, body contains
"Bob Test", "admin", and "99999". Reproduced exactly.

Proof capsule:
- request: GET http://127.0.0.1:8901/user?id=2
- response: 200, body contains Bob Test, role admin, balance 99999
- replay: curl -s "http://127.0.0.1:8901/user?id=2"
- severity recommendation: high, unchanged. An unauthenticated
  request returns another user's record, including an admin role
  and balance.

## 2. api-bola-user-2, verified, confidence 5

Finding record: GET /api/users/2, expected 401, actual 200 with
the same Bob Test record as JSON.

Verification, re-run: GET /api/users/2 returned 200,
{"id": 2, "name": "Bob Test", "email": "bob@test.local",
"role": "admin", "balance": 99999}. Reproduced exactly.

Proof capsule:
- request: GET http://127.0.0.1:8901/api/users/2
- response: 200, JSON above
- replay: curl -s "http://127.0.0.1:8901/api/users/2"
- note: same root cause as idor-user-profile, the missing
  ownership check. Report as one finding with two proofs,
  per the ensemble rule, not as two separate highs.

## 3. reflected-xss-search, verified, confidence 5

Finding record: GET /search?q=cjxss123<b>probe</b>456, marker
cjxss123, expected the marker escaped, actual raw <b>probe</b>
in the response.

Verification, re-run: GET /search?q=cjxss123%3Cb%3Eprobe%3C%2Fb%3E456
returned 200, body contains raw <b>probe</b>. Reproduced exactly.

Proof capsule:
- request: GET http://127.0.0.1:8901/search?q=cjxss123%3Cb%3Eprobe%3C%2Fb%3E456
- response: 200, raw <b>probe</b> present, marker cjxss123 present
- replay: curl -s "http://127.0.0.1:8901/search?q=cjxss123%3Cb%3Eprobe%3C%2Fb%3E456"
- severity recommendation: medium, unchanged. Reflected, needs
  a victim to click, no stored payload.

## 4. idor-user-999, rejected, confidence 5

Finding record (deliberately wrong, to test the rejected verdict):
GET /user?id=999 returns a user record.

Verification, re-run: GET /user?id=999 returned 404,
"<h1>User not found</h1>". No user record, no leak. The
behaviour is correct, the finding is not a vulnerability.

Proof capsule:
- request: GET http://127.0.0.1:8901/user?id=999
- response: 404, User not found
- replay: curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8901/user?id=999"
- note: rejected, do not re-report. A nonexistent id is handled
  correctly, which also shows the IDOR is about existing ids,
  not about error handling.
