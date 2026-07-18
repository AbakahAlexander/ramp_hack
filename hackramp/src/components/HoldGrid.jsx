import { buildWallXml, holdShape, parseWallXml } from "../wallXml";

/**
 * Independent cartoon wall — SVG holds from scene XML (not a photo overlay).
 * Focus one route or show all; optimize later by editing XML.
 */
export function HoldGrid({
  routes,
  walls,
  selectedWallKey,
  selectedRouteId,
  onSelectWall,
  onSelectRoute,
  sceneXml,
}) {
  const wallMeta = (walls || []).find((w) => w.key === selectedWallKey) || walls?.[0];
  const focusRoutes = selectedRouteId
    ? routes.filter((r) => r.id === selectedRouteId)
    : routes;

  let parsed = null;
  if (sceneXml) {
    try {
      parsed = parseWallXml(sceneXml);
    } catch {
      parsed = null;
    }
  }

  const xmlRoutes =
    parsed?.routes?.length > 0
      ? parsed.routes
          .map((pr) => {
            const match = routes.find((r) => r.id === pr.id) || routes.find((r) => r.colorName === pr.colorName);
            return {
              ...pr,
              id: match?.id || pr.id,
              status: match?.status || "Healthy",
            };
          })
          .filter((r) => !selectedRouteId || r.id === selectedRouteId)
      : null;

  const drawRoutes =
    xmlRoutes && xmlRoutes.length
      ? xmlRoutes
      : focusRoutes.map((r) => ({
          id: r.id,
          name: r.name,
          colorName: r.colorName,
          color: r.color,
          grade: r.grade,
          holds: (r.holds || []).map((h) => ({
            ...h,
            shape: h.shape || holdShape(h.hold_type),
          })),
        }));

  const displayXml =
    sceneXml ||
    buildWallXml(routes, { wallName: wallMeta?.name || "Wall", wallId: wallMeta?.id || "" });

  return (
    <div className="boards boards-cartoon">
      <div
        className="board board-cartoon selected"
        role="region"
        aria-label="Cartoon route board"
      >
        <div className="board-head">
          <span className="board-name">{wallMeta?.name || parsed?.wallName || "Wall"}</span>
          <span className="board-meta">cartoon · XML</span>
        </div>
        <div className="cartoon-stage">
          <svg className="cartoon-svg" viewBox="0 0 100 100" role="img">
            {/* wall face */}
            <rect x="0" y="0" width="100" height="100" fill="#d8d4cc" />
            <rect x="0" y="0" width="100" height="100" fill="url(#boltGrid)" opacity="0.35" />
            {/* crash pad */}
            <rect x="0" y="94" width="100" height="6" fill="#2a4a8a" />
            <defs>
              <pattern id="boltGrid" width="4" height="4" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="0.35" fill="#5a5a5a" />
              </pattern>
            </defs>
            {drawRoutes.map((route) =>
              (route.holds || []).map((h, i) => (
                <HoldShape
                  key={`${route.id}-${h.sequence_index}-${i}`}
                  hold={h}
                  color={route.color}
                  dimmed={Boolean(selectedRouteId && route.id !== selectedRouteId)}
                  onClick={() => {
                    onSelectWall?.(route.wallKey || selectedWallKey);
                    onSelectRoute?.(route.id);
                  }}
                />
              )),
            )}
          </svg>
        </div>
        <div className="board-routes">
          {routes.map((r) => (
            <button
              key={r.id}
              type="button"
              className={selectedRouteId === r.id ? "route-chip active" : "route-chip"}
              onClick={() => {
                onSelectWall?.(r.wallKey);
                onSelectRoute?.(r.id);
              }}
            >
              <i style={{ background: r.color }} />
              {r.colorName || r.name} {r.grade}
            </button>
          ))}
        </div>
        <details className="xml-drawer">
          <summary>Scene XML ({routes.length} routes) — edit to optimize</summary>
          <pre>{displayXml}</pre>
        </details>
      </div>
    </div>
  );
}

function HoldShape({ hold, color, dimmed, onClick }) {
  const cx = (Number(hold.x) || 0.5) * 100;
  const cy = (Number(hold.y) || 0.5) * 100;
  const size = Number(hold.size) || 0.05;
  const w = Math.max(1.5, Math.min(18, size * 55));
  const h = w;
  const shape = hold.shape || holdShape(hold.hold_type);
  const opacity = dimmed ? 0.22 : 1;
  const common = {
    fill: color,
    stroke: "#1a1a1a",
    strokeWidth: 0.35,
    opacity,
    style: { cursor: "pointer" },
    onClick,
  };

  if (shape === "triangle") {
    const pts = `${cx},${cy - h / 2} ${cx + w / 2},${cy + h / 2} ${cx - w / 2},${cy + h / 2}`;
    return <polygon points={pts} {...common} />;
  }
  if (shape === "rounded_rect") {
    return <rect x={cx - w / 2} y={cy - h / 2} width={w} height={h} rx={w * 0.25} {...common} />;
  }
  if (shape === "oval") {
    return <ellipse cx={cx} cy={cy} rx={w / 2} ry={h / 2.4} {...common} />;
  }
  if (shape === "polygon") {
    const pts = [
      [cx, cy - h / 2],
      [cx + w / 2, cy - h / 6],
      [cx + w / 3, cy + h / 2],
      [cx - w / 3, cy + h / 2],
      [cx - w / 2, cy - h / 6],
    ]
      .map(([x, y]) => `${x},${y}`)
      .join(" ");
    return <polygon points={pts} {...common} />;
  }
  return <circle cx={cx} cy={cy} r={w / 2} {...common} />;
}
