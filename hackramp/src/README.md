# Crux frontend (staff dashboard)

## Run

```bash
cd hackramp/src
npm install
npm run dev
```

In dev, `/api` is proxied to the backend (default: Koyeb). Override:

```
VITE_PROXY_TARGET=http://127.0.0.1:8000
```

Or set `VITE_API_URL` to hit an API directly (skips proxy).

## Extract routes from one photo

**Add route** → upload a wall photo (no color picker).

Backend auto-detects every colored line → returns:

- One DB route per color
- Editable `<wall>` **scene XML** (positions, shapes, colors)

The dashboard draws an independent **cartoon SVG** from that XML (not a photo highlight). Optimize later by rewriting the XML.

## Local backend (no redeploy)

1. Start API: `cd backend && uvicorn app.main:app --reload --port 8000`
2. Start UI: `cd hackramp/src && npm run dev`

Vite proxies `/api` → `http://127.0.0.1:8000` by default.
