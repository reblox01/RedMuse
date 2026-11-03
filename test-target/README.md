# Test target

Intentionally vulnerable, localhost only, fake data only. Run it, test
it, kill it. Never deploy it anywhere public.

```bash
python3 app.py        # serves http://127.0.0.1:8901
python3 app.py 8902   # another port
```

Planted flaws:

- IDOR on `/user?id=` (no ownership check)
- Reflected XSS on `/search?q=` (unescaped reflection)
- Open redirect on `/redirect?url=`
- API BOLA on `/api/users/<id>` (no auth)
- Missing security headers (info level)

A muse-strix quick run against it should confirm all four real flaws
plus the headers note, and produce the sample report in `examples/`.
