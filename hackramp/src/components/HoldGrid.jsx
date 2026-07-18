import { WALLS as DEFAULT_WALLS, isLitStatus } from "../data/wallsConfig";

export function HoldGrid({
  routes,
  walls = DEFAULT_WALLS,
  selectedWallKey,
  selectedRouteId,
  onSelectWall,
  onSelectRoute,
}) {
  const boards = walls?.length ? walls : DEFAULT_WALLS;
  return (
    <div className="boards">
      {boards.map((wall) => (
        <WallPanel
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

function WallPanel({
  wall,
  routes,
  selected,
  selectedRouteId,
  onSelectWall,
  onSelectRoute,
}) {
  const total = wall.cols * wall.rows;
  const focusRoute = selectedRouteId ? routes.find((r) => r.id === selectedRouteId) : null;

  const cellMap = new Map();
  for (const route of routes) {
    const selected = route.id === selectedRouteId;
    if (!isLitStatus(route.status) && !selected) continue;
    if (route.status === "Strip soon" && !selected) continue;
    if (focusRoute && route.id !== focusRoute.id) continue;
    for (const idx of route.cells) {
      const list = cellMap.get(idx) ?? [];
      list.push(route);
      cellMap.set(idx, list);
    }
  }

  return (
    <div
      className={selected ? "board selected" : "board"}
      onClick={onSelectWall}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") onSelectWall();
      }}
      role="button"
      tabIndex={0}
    >
      <div className="board-head">
        <span className="board-name">{wall.name}</span>
        <span className="board-meta">{wall.zone}</span>
      </div>
      <div
        className="grid"
        style={{ gridTemplateColumns: `repeat(${wall.cols}, 1fr)` }}
        onClick={(e) => e.stopPropagation()}
      >
        {Array.from({ length: total }, (_, i) => {
          const hits = cellMap.get(i) ?? [];
          const primary = hits[0];
          const lit = Boolean(primary);
          return (
            <button
              key={i}
              type="button"
              className={lit ? "hold lit" : "hold"}
              style={
                lit
                  ? {
                      background: primary.color,
                      boxShadow: `0 0 12px ${primary.color}99, inset 0 0 0 1px rgba(255,255,255,0.28)`,
                    }
                  : undefined
              }
              title={lit ? `${primary.colorName || primary.name} ${primary.grade}` : undefined}
              onClick={() => {
                onSelectWall();
                onSelectRoute(primary ? primary.id : null);
              }}
            />
          );
        })}
      </div>
      <div className="board-routes">
        {routes.map((r) => (
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
