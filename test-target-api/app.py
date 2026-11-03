#!/usr/bin/env python3
"""muse-strix API test target. INTENTIONALLY VULNERABLE. Localhost only.

A tiny fake JSON API (Python standard library only) with four planted
API flaws so a muse-strix API run can prove itself end to end:

- BOLA on GET /api/v1/users/<id> (no auth, any id returns that user)
- Excessive data exposure on GET /api/v1/users (list returns internal
  fields the client never shows)
- Mass assignment on POST /api/v1/users (role field accepted from the
  client, so a caller can create an admin)
- Broken function level authorization on GET /api/v1/admin/stats
  (admin endpoint with no auth check)

Fake data only. No real users, no database.
NEVER deploy this anywhere public. Run it on localhost, test it, kill it.

Usage: python3 app.py [port]   (default port 8902)
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

USERS = {
    "1": {"id": 1, "name": "Alice Test", "email": "alice@test.local",
          "role": "user", "salary_band": "B2",
          "internal_note": "VIP support case open"},
    "2": {"id": 2, "name": "Bob Test", "email": "bob@test.local",
          "role": "admin", "salary_band": "E1",
          "internal_note": "Has production root access"},
}
NEXT_ID = [3]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, obj, status=200):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send({"endpoints": [
                "GET /api/v1/users",
                "GET /api/v1/users/<id>",
                "POST /api/v1/users",
                "GET /api/v1/admin/stats",
            ]})
        elif self.path == "/api/v1/users":
            # PLANTED FLAW: list returns internal fields.
            self._send(list(USERS.values()))
        elif self.path.startswith("/api/v1/users/"):
            uid = self.path.rsplit("/", 1)[-1]
            user = USERS.get(uid)
            if not user:
                self._send({"error": "not found"}, status=404)
                return
            # PLANTED FLAW: no auth, any id returns that user.
            self._send(user)
        elif self.path == "/api/v1/admin/stats":
            # PLANTED FLAW: admin endpoint with no auth check.
            self._send({"total_users": len(USERS),
                        "admin_count": 1,
                        "revenue_estimate": 42000})
        else:
            self._send({"error": "not found"}, status=404)

    def do_POST(self):
        if self.path == "/api/v1/users":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            # PLANTED FLAW: mass assignment, role accepted from client.
            user = {"id": NEXT_ID[0],
                    "name": body.get("name", "New Test"),
                    "email": body.get("email", "new@test.local"),
                    "role": body.get("role", "user")}
            USERS[str(NEXT_ID[0])] = user
            NEXT_ID[0] += 1
            self._send(user, status=201)
        else:
            self._send({"error": "not found"}, status=404)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8902
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"muse-strix API test target on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
