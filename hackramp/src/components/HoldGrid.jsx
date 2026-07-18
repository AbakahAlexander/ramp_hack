import { WALLS as DEFAULT_WALLS, isLitStatus } from "../data/wallsConfig";
import { API_BASE } from "../api";

function photoSrc(url) {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  return `${API_BASE}${url}`;
}

/** Spatial heatmap board — soft blobs at continuous x/y with size, optionally on wall photo. */
export function HoldGrid({
  routes,
  walls = DEFAULT_WALLS,
  selectedWallKey,
  selectedRouteId,
  onSelectWall,
  onSelectRoute,
}) {
  const boards = walls?.length ? walls : DEFAULT_WALLS;
  const focus = selectedRouteId ? routes.find((r) => r.id === selectedRouteId) : null;

  // When a route with a photo is selected, show one large heatmap panel
  if (focus?.photoUrl) {
    return (
      <div className="boards boards-heatmap">
        <HeatmapPanel
          route={focus}
          wall={boards.find((w) => w.key === focus.wallKey) || boards[0]}
          selected
          onSelectWall={() => onSelectWall(focus.wallKey)}
          onSelectRoute={onSelectRoute}
          routes={routes.filter((r) => r.wallKey === focus.wallKey)}
          selectedRouteId={selectedRouteId}
        />
      </div>
    );
  }

  return (
    <div className="boards">
      {boards.map((wall) => (
        <HeatmapPanel
          key={wall.key}
          wall={wall}
          routes={routes.filter((r) => r.wallKey === wall.key)}
          selected={selectedWallKey === wall.key}
          selectedRouteId={selectedRouteId}
          onSelectWall={() => onSelectWall(wall.key)}
          onSelectRoute={onSelectRoute}
        />
      ))}
    </div>
  );
}

function HeatmapPanel({
  wall,
  routes = [],
  route,
  selected,
  selectedRouteId,
  onSelectWall,
  onSelectRoute,
}) {
  const primary = route || (selectedRouteId ? routes.find((r) => r.id === selectedRouteId) : null);
  const showRoutes = route ? [route] : routes;
  const bg = photoSrc(primary?.photoUrl);

  const blobs = [];
  for (const r of showRoutes) {
    const active = !selectedRouteId || r.id === selectedRouteId;
    if (!isLitStatus(r.status) && r.id !== selectedRouteId) continue;
    if (selectedRouteId && r.id !== selectedRouteId) continue;
    for (const h of r.holds || []) {
      const x = h.x ?? ((h.col + 0.5) / (wall?.cols || 8));
      const y = h.y ?? ((h.row + 0.5) / (wall?.rows || 10));
      const size = h.size ?? 0.05;
      blobs.push({
        key: `${r.id}-${h.sequence_index}-${h.cell_index}`,
        x,
        y,
        size,
        color: r.color,
        routeId: r.id,
        label: `${r.colorName || r.name} #${(h.sequence_index ?? 0) + 1}`,
        active,
      });
    }
  }

  return (
    <div
      className={selected ? "board board-heat selected" : "board board-heat"}
      onClick={onSelectWall}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") onSelectWall();
      }}
      role="button"
      tabIndex={0}
    >
      <div className="board-head">
        <span className="board-name">{wall?.name || primary?.wall || "Wall"}</span>
        <span className="board-meta">{wall?.zone || "heatmap"}</span>
      </div>
      <div
        className={bg ? "heat-stage has-photo" : "heat-stage"}
        style={bg ? { backgroundImage: `url(${bg})` } : undefined}
        onClick={(e) => e.stopPropagation()}
      >
        {!bg && <div className="heat-grid-bg" aria-hidden />}
        <svg className="heat-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
          <defs>
            {blobs.map((b) => (
              <radialGradient key={`g-${b.key}`} id={`blob-${b.key}`} cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor={b.color} stopOpacity="0.95" />
                <stop offset="55%" stopColor={b.color} stopOpacity="0.45" />
                <stop offset="100%" stopColor={b.color} stopOpacity="0" />
              </radialGradient>
            ))}
          </defs>
          {blobs.map((b) => {
            const r = Math.max(1.2, b.size * 55);
            return (
              <circle
                key={b.key}
                className="heat-blob"
                cx={b.x * 100}
                cy={b.y * 100}
                r={r}
                fill={`url(#blob-${b.key})`}
                onClick={() => {
                  onSelectWall();
                  onSelectRoute(b.routeId);
                }}
              >
                <title>{b.label}</title>
              </circle>
            );
          })}
        </svg>
        {!blobs.length && <div className="heat-empty">No holds mapped yet</div>}
      </div>
      <div className="board-routes">
        {(route ? [route] : routes).map((r) => (
          <button
            key={r.id}
            type="button"
            className={
              selectedRouteId === r.id
                ? "route-chip active"
                : isLitStatus(r.status)
                  ? "route-chip"
                  : "route-chip dim"
            }
            onClick={(e) => {
              e.stopPropagation();
              onSelectWall();
              onSelectRoute(r.id);
            }}
          >
            <i style={{ background: r.color }} />
            {r.colorName || r.name} {r.grade}
          </button>
        ))}
      </div>
    </div>
  );
}
