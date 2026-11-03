# API test target

Intentionally vulnerable, localhost only, fake data only. Run it, test
it, kill it. Never deploy it anywhere public.

```bash
python3 app.py        # serves http://127.0.0.1:8902
```

Planted flaws:

- BOLA on `GET /api/v1/users/<id>` (no auth)
- Excessive data exposure on `GET /api/v1/users` (internal fields in
  the list response)
- Mass assignment on `POST /api/v1/users` (role accepted from client)
- Broken function level authorization on `GET /api/v1/admin/stats`
  (admin endpoint, no auth)

A muse-strix API run against it should confirm all four, and produce
the sample report in `examples/`.
