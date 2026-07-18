# Crux frontend (staff dashboard)

## Run

```bash
cd hackramp/src
npm install
npm run dev
```

Optional: create `.env` in this folder:

```
VITE_API_URL=https://holy-merrill-tormame-aafedec0.koyeb.app
```

For local API: `VITE_API_URL=http://localhost:8000`

## Demo flow

1. Dashboard shows **static** prepopulated routes (not loaded from API inventory).
2. Paste climber feedback in the feedback box (sample text is preloaded).
3. Click **Analyze with AI** → `POST /api/v1/insights/analyze`.
4. Click a route — the detail panel shows **keep / monitor / change out** plus what to change it to.

Backend needs `OPENAI_API_KEY` on Koyeb (or local `.env`). Without a key, the API uses a deterministic fallback so the UI still works.
