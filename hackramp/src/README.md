# Crux frontend (staff dashboard)

## Run

From this folder (or use the working Vite app under `../wall-heatmap-options` if installs are flaky):

```bash
npm install
npm run dev
```

## Backend contract (next)

Wire mock `routeData` in `App.jsx` to:

- `GET /api/v1/walls`
- `GET /api/v1/routes`

Route objects used by the hold board need:

- `id`, `name`, `grade`, `wall` / `wallKey`, `zone`, `color`, `status`
- `cells: number[]` — grid indices to light (0..cols*rows-1)

Wall keys today: `slab` | `steep` | `vertical` (see `data/wallsConfig.js`).

## Notes

- Gym view = lit square hold boards (`components/HoldGrid.jsx`)
- List + detail panel stay in sync with selected route
- Still mock data until API is connected
