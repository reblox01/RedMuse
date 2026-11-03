#!/usr/bin/env python3
"""redmuse test target. INTENTIONALLY VULNERABLE. Localhost only.

A tiny fake app (Python standard library only, no dependencies) with
four planted flaws so a redmuse run can prove itself end to end:

- IDOR on /user?id= (no ownership check, any id returns that user)
- Reflected XSS on /search?q= (query reflected unescaped)
- Open redirect on /redirect?url=
- API BOLA on /api/users/<id> (no auth, any id returns that user)

Fake data only. No real users, no database, no auth that matters.
NEVER deploy this anywhere public. Run it on localhost, test it, kill it.

Usage: python3 app.py [port]   (default port 8901)
"""
import html
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

USERS = {
    "1": {"id": 1, "name": "Alice Test", "email": "alice@test.local",
          "role": "user", "balance": 100},
    "2": {"id": 2, "name": "Bob Test", "email": "bob@test.local",
          "role": "admin", "balance": 99999},
    "3": {"id": 3, "name": "Carol Test", "email": "carol@test.local",
          "role": "user", "balance": 50},
}

INDEX = """<html><head><title>redmuse test target</title></head><body>
<h1>redmuse test target (localhost only)</h1>
<ul>
<li><a href="/user?id=1">/user?id=1</a> (try id=2, id=3)</li>
<li><a href="/search?q=hello">/search?q=hello</a></li>
<li><a href="/redirect?url=https://example.com">/redirect?url=...</a></li>
<li><a href="/api/users/1">/api/users/1</a> (try /api/users/2)</li>
</ul>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, body, status=200, ctype="text/html"):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        if parsed.path == "/":
            self._send(INDEX)
        elif parsed.path == "/user":
            uid = qs.get("id", ["1"])[0]
            user = USERS.get(uid)
            if not user:
                self._send("<h1>User not found</h1>", status=404)
                return
            # PLANTED FLAW: no ownership check, any id returns that user.
            self._send(
                f"<h1>{html.escape(user['name'])}</h1>"
                f"<p>email: {html.escape(user['email'])}</p>"
                f"<p>role: {html.escape(user['role'])}</p>"
                f"<p>balance: {user['balance']}</p>"
            )
        elif parsed.path == "/search":
            q = qs.get("q", [""])[0]
            # PLANTED FLAW: query reflected without escaping.
            self._send(f"<h1>Results for: {q}</h1><p>No results.</p>")
        elif parsed.path == "/redirect":
            url = qs.get("url", ["https://example.com"])[0]
            # PLANTED FLAW: open redirect, any url accepted.
            self.send_response(302)
            self.send_header("Location", url)
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif parsed.path.startswith("/api/users/"):
            uid = parsed.path.rsplit("/", 1)[-1]
            user = USERS.get(uid)
            if not user:
                self._send(json.dumps({"error": "not found"}), status=404,
                           ctype="application/json")
                return
            # PLANTED FLAW: no auth, any id returns that user.
            self._send(json.dumps(user), ctype="application/json")
        else:
            self._send("<h1>Not found</h1>", status=404)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8901
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"redmuse test target on http://127.0.0.1:{port} (localhost only)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
