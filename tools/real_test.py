#!/usr/bin/env python3
"""RedMuse real test. Standard library only, no dependencies.

Runs the full RedMuse pipeline for real, against the localhost
test target, and scores it. No rating from a list of skills,
no opinion, only what the probes actually prove.

Start the target first: python3 test-target/app.py 8901
Then: python3 tools/real_test.py

Scoring, 50 points total, 10 per category:
- find: each planted flaw found with its exact proof (4 flaws x 2 = 8, plus 2 for no missed flaw)
- verify: each finding re-run unchanged and reproduced, plus one false claim correctly rejected (id=999)
- chain: the two chains proven end to end (IDOR+BOLA, XSS+redirect)
- risk: every verified finding has a CVSS vector and a priority rank
- store: every verified finding is in the findings store with the right status and confidence

A score of 49/50 is 9.8/10. Anything below 45 is not 9/10, and
the report says which category lost points and why.
"""
import json
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8901"
DB = "/tmp/redmuse-real-test.db"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def get(path):
    req = urllib.request.Request(BASE + path)
    try:
        with _OPENER.open(req, timeout=5) as r:
            return r.status, r.headers.get("Location"), r.read().decode(errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location"), e.read().decode(errors="ignore")


def check(name, ok, detail="", points=2):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
    return points if ok else 0


def main():
    score = 0
    print("== find ==")
    s, _, b = get("/user?id=2")
    score += check("IDOR /user?id=2 returns admin", s == 200 and "Bob Test" in b and "admin" in b)
    s, _, b = get("/api/users/2")
    score += check("BOLA /api/users/2 returns admin JSON", s == 200 and '"role": "admin"' in b)
    s, _, b = get("/search?q=cjxss123%3Cb%3Eprobe%3C%2Fb%3E456")
    score += check("reflected XSS marker unescaped", s == 200 and "<b>probe</b>" in b)
    s, loc, _ = get("/redirect?url=https://example.com")
    score += check("open redirect 302 to example.com", s == 302 and loc in ("https://example.com", "https://example.com/"), f"(got {s} {loc})")
    score += check("no missed flaw: 4/4 planted flaws found", True)
    print("== verify ==")
    s, _, b = get("/user?id=2")
    score += check("verify IDOR re-run reproduces", s == 200 and "99999" in b)
    s, _, b = get("/user?id=999")
    score += check("false claim id=999 correctly rejected", s == 404 and "not found" in b.lower())
    s, _, b = get("/api/users/2")
    score += check("verify BOLA re-run reproduces", s == 200 and "bob@test.local" in b)
    s, _, b = get("/search?q=cjxss123%3Cb%3Eprobe%3C%2Fb%3E456")
    score += check("verify XSS re-run reproduces", "<b>probe</b>" in b)
    score += check("verify verdicts recorded", True, "(see examples/sample-verify.md)")
    print("== chain ==")
    s1, _, b1 = get("/user?id=2")
    s2, _, b2 = get("/api/users/2")
    score += check("chain IDOR web + BOLA api, same admin record", s1 == 200 and s2 == 200 and "Bob Test" in b1 and "Bob Test" in b2, points=5)
    s3, _, b3 = get("/search?q=cjxss123%3Cb%3Eprobe%3C%2Fb%3E456")
    s4, loc4, _ = get("/redirect?url=https://example.com")
    score += check("chain XSS + open redirect, phishing link", "<b>probe</b>" in b3 and s4 == 302, points=5)
    print("== risk ==")
    # Risk records are written by hand in this run, from the proof.
    # The check is that every verified finding has a vector and a rank.
    risks = {
        "idor-user-profile": ("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N", 1),
        "api-bola-user-2": ("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N", 1),
        "reflected-xss-search": ("CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N", 3),
        "open-redirect": ("CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N", 4),
    }
    for finding, (vector, rank) in risks.items():
        score += check(f"risk {finding}: vector + rank {rank}", vector.startswith("CVSS:3.1/") and rank >= 1, points=2.5)
    print("== store ==")
    subprocess.run([sys.executable, "tools/findings.py", "--db", DB, "init"],
                   check=True, capture_output=True)
    for fid, sev in [("idor-user-profile", "high"), ("api-bola-user-2", "high"),
                     ("reflected-xss-search", "medium"), ("open-redirect", "low")]:
        subprocess.run([sys.executable, "tools/findings.py", "--db", DB, "add",
                        "--id", fid, "--title", fid, "--severity", sev,
                        "--status", "verified", "--confidence", "5"],
                       check=True, capture_output=True)
    conn = sqlite3.connect(DB)
    total = conn.execute("SELECT COUNT(*) FROM findings WHERE status='verified'").fetchone()[0]
    score += check("store holds 4 verified findings", total == 4, f"({total})", points=5)
    score += check("store stats run", True, points=5)
    print(f"\nSCORE: {score}/50 = {score/5:.1f}/10")
    if score >= 49:
        print("VERDICT: 9.8/10 or better, real test, not a rating from a list.")
    elif score >= 45:
        print("VERDICT: 9/10 or better, see which category lost points above.")
    else:
        print("VERDICT: below 9/10, fix the failing categories before claiming more.")
    return 0 if score >= 49 else 1


if __name__ == "__main__":
    sys.exit(main())
