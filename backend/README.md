# Crux API (FastAPI)

Backend for **Crux**. Swagger: `/docs` · OpenAPI: `/openapi.json`

**Hackathon MVP: no auth.** All endpoints are open; a demo gym is seeded on startup.

## Quick start

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs

## Tests

```bash
pytest -q
```

## Database (hackathon)

Default is **SQLite file on the service** (`crux.db`) — fine for demo, but data can be lost on Koyeb redeploy/restart unless you attach a volume or use hosted Postgres.

**Recommended for Koyeb:** create a **Koyeb Postgres** (or Supabase) and set `DATABASE_URL=postgresql://...`. Same API either way.

You do **not** need Supabase unless you want a managed DB outside Koyeb.

## Deploy on Koyeb

1. Sign up: https://app.koyeb.com/auth/signup
2. New App → deploy from GitHub (this repo) or Docker, root directory `backend`
3. Env vars:
   - `SEED_ON_STARTUP=true`
   - `CORS_ORIGINS=*` (or your frontend URL)
   - `DATABASE_URL` — optional; omit for SQLite, or paste Postgres URL
4. Share `https://<app>.koyeb.app/docs` with frontend

## Photo field

Design asks for a **route photo**. MVP stores optional `photo_url` (string link). No file upload yet — frontend can omit it or use any image URL.
