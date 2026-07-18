# Crux frontend (staff dashboard)

## Run

```bash
cd hackramp/src
npm install
npm run dev
```

Optional `.env`:

```
VITE_API_URL=https://holy-merrill-tormame-aafedec0.koyeb.app
```

## Data source

Routes and hold sequences load from the API (`GET /api/v1/routes`, `GET /api/v1/walls`).  
No hardcoded route inventory — the list is empty until you add one.

## Add route from photo

Use **Add route** in the dashboard (or `POST /api/v1/routes/from-image`):

1. Pick a wall
2. Upload a photo of the climb
3. Vision AI returns a normalized hold grid (`row` / `col` / `hold_type`) and persists the route

Optional overrides: name, color, grade.

Manual create still works via `POST /api/v1/routes` with an explicit `holds` list.

## AI insights

Paste feedback → Analyze → click a route for keep / change-out guidance.
