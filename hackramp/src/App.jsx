import { useEffect, useMemo, useState } from "react";
import { HoldGrid } from "./components/HoldGrid";
import {
  API_BASE,
  SAMPLE_FEEDBACK,
  analyzeFeedback,
  clearAllRoutes,
  createRoutesFromImage,
  fetchRoutes,
  fetchWalls,
} from "./api";
import "./styles.css";
import "./hold-board.css";
import "./insights.css";

const initials = (name) =>
  String(name || "?")
    .split(" ")
    .map((part) => part[0])
    .join("");

function Icon({ name, size = 18, stroke = 1.8 }) {
  const paths = {
    grid: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </>
    ),
    routes: (
      <>
        <path d="M5 4h14" />
        <path d="M5 10h14" />
        <path d="M5 16h10" />
        <circle cx="3" cy="4" r=".7" fill="currentColor" />
        <circle cx="3" cy="10" r=".7" fill="currentColor" />
        <circle cx="3" cy="16" r=".7" fill="currentColor" />
      </>
    ),
    map: (
      <>
        <path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z" />
        <path d="M9 3v15M15 6v15" />
      </>
    ),
    chart: (
      <>
        <path d="M4 19V5" />
        <path d="M4 19h16" />
        <path d="m7 15 4-5 3 2 5-7" />
      </>
    ),
    settings: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.12 2.12-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V20.3h-3v-.08A1.7 1.7 0 0 0 10.68 18.66a1.7 1.7 0 0 0-1.88.34l-.06.06-2.12-2.12.06-.06A1.7 1.7 0 0 0 7.02 15a1.7 1.7 0 0 0-1.56-1.03H5.4v-3h.08A1.7 1.7 0 0 0 7.02 9.94a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.12-2.12.06.06a1.7 1.7 0 0 0 1.88.34 1.7 1.7 0 0 0 1.03-1.56V4.64h3v.08a1.7 1.7 0 0 0 1.03 1.56 1.7 1.7 0 0 0 1.88-.34l.06-.06 2.12 2.12-.06.06a1.7 1.7 0 0 0-.34 1.88 1.7 1.7 0 0 0 1.56 1.03h.08v3h-.08A1.7 1.7 0 0 0 19.4 15Z" />
      </>
    ),
    search: (
      <>
        <circle cx="10.8" cy="10.8" r="6.2" />
        <path d="m16 16 4 4" />
      </>
    ),
    chevron: <path d="m9 18 6-6-6-6" />,
    plus: (
      <>
        <path d="M12 5v14" />
        <path d="M5 12h14" />
      </>
    ),
    filter: (
      <>
        <path d="M4 6h16" />
        <path d="M7 12h10" />
        <path d="M10 18h4" />
      </>
    ),
    bell: (
      <>
        <path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
        <path d="M10 21h4" />
      </>
    ),
    dots: (
      <>
        <circle cx="5" cy="12" r="1.25" fill="currentColor" />
        <circle cx="12" cy="12" r="1.25" fill="currentColor" />
        <circle cx="19" cy="12" r="1.25" fill="currentColor" />
      </>
    ),
    arrow: (
      <>
        <path d="M5 12h14" />
        <path d="m13 6 6 6-6 6" />
      </>
    ),
    info: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 11v5" />
        <path d="M12 8h.01" />
      </>
    ),
    calendar: (
      <>
        <rect x="3.5" y="5" width="17" height="15.5" rx="2" />
        <path d="M7.5 3v4M16.5 3v4M3.5 10h17" />
      </>
    ),
  };
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={stroke}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  );
}

function recommendationLabel(rec) {
  if (rec === "keep") return "Keep";
  if (rec === "change_out") return "Change out";
  if (rec === "monitor") return "Monitor";
  return null;
}

function RouteCard({ route, selected, onClick, insight }) {
  const aiStatus = recommendationLabel(insight?.recommendation);
  return (
    <button className={`route-card ${selected ? "selected" : ""}`} onClick={() => onClick(route.id)}>
      <span className="route-swatch" style={{ background: route.color }} />
      <span className="route-main">
        <span className="route-name-line">
          <strong>{route.name}</strong>
          <span className="grade">{route.grade}</span>
        </span>
        <span className="route-meta">
          {route.wall} · {route.style}
        </span>
      </span>
      <span
        className={`route-status ${(aiStatus || route.status).toLowerCase().replace(" ", "-")}`}
      >
        {aiStatus || route.status}
      </span>
      <Icon name="chevron" size={15} />
    </button>
  );
}

function GymHoldView({ routes, walls, selected, selectRoute, sceneXml }) {
  const selectedRoute = routes.find((r) => r.id === selected);
  const wallKey = selectedRoute?.wallKey ?? walls[0]?.key ?? "slab";

  return (
    <section className="gym-map gym-hold-view" aria-label="Cartoon route board">
      <div className="map-heading">
        <span>Cartoon board</span>
        <small>Independent SVG from scene XML — shapes, colors, positions (not a photo highlight)</small>
      </div>
      <HoldGrid
        routes={routes}
        walls={walls}
        selectedWallKey={wallKey}
        selectedRouteId={selected}
        onSelectWall={() => {}}
        onSelectRoute={selectRoute}
        sceneXml={sceneXml}
      />
    </section>
  );
}

function AddRouteModal({ walls, onClose, onCreated }) {
  const [wallId, setWallId] = useState(walls[0]?.id || "");
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!wallId && walls[0]?.id) setWallId(walls[0].id);
  }, [walls, wallId]);

  const submit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Choose a wall photo.");
      return;
    }
    if (!wallId) {
      setError("Select a wall.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const batch = await createRoutesFromImage({ wallId, file });
      onCreated(batch);
    } catch (err) {
      setError(err.message || "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="modal-panel"
        role="dialog"
        aria-labelledby="add-route-title"
        onClick={(ev) => ev.stopPropagation()}
      >
        <div className="modal-head">
          <div>
            <p className="eyebrow">WALL PHOTO</p>
            <h2 id="add-route-title">Extract all routes</h2>
            <p>
              One image → every colored route auto-detected into editable scene XML and the cartoon
              board. No color picking.
            </p>
          </div>
          <button type="button" className="icon-button" aria-label="Close" onClick={onClose}>
            ×
          </button>
        </div>
        <form className="modal-form" onSubmit={submit}>
          <label>
            Wall
            <select value={wallId} onChange={(e) => setWallId(e.target.value)} required>
              {walls.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name} ({w.zone})
                </option>
              ))}
            </select>
          </label>
          <label>
            Wall photo
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              required
            />
          </label>
          {error && <p className="modal-error">{error}</p>}
          <div className="modal-actions">
            <button type="button" className="ghost" onClick={onClose} disabled={busy}>
              Cancel
            </button>
            <button type="submit" className="primary" disabled={busy || !walls.length}>
              {busy ? "Detecting routes…" : "Extract routes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function RouteDetails({ route, insight }) {
  const aiStatus = recommendationLabel(insight?.recommendation);
  return (
    <aside className="route-details">
      <div className="detail-topline">
        <span
          className={`route-status ${(aiStatus || route.status).toLowerCase().replace(" ", "-")}`}
        >
          {aiStatus || route.status}
        </span>
        <button aria-label="More actions" className="icon-button">
          <Icon name="dots" />
        </button>
      </div>
      <div className="detail-route-title">
        <span className="large-swatch" style={{ background: route.color }} />
        <div>
          <h2>{route.name}</h2>
          <p>
            {route.identifier} · {route.grade}
          </p>
        </div>
      </div>
      <div className="detail-location">
        <Icon name="map" size={16} />
        <span>
          {route.wall}, {route.zone}
        </span>
      </div>
      <div className="details-grid">
        <div>
          <small>Setter</small>
          <span>
            <b className="avatar mini">{initials(route.setter)}</b>
            {route.setter}
          </span>
        </div>
        <div>
          <small>Set date</small>
          <span>
            <Icon name="calendar" size={15} />
            {route.set}
          </span>
        </div>
        <div>
          <small>On wall</small>
          <span>{route.age}</span>
        </div>
        <div>
          <small>Style</small>
          <span>{route.style}</span>
        </div>
        <div>
          <small>Holds lit</small>
          <span>{route.cells?.length ?? 0}</span>
        </div>
      </div>

      {insight ? (
        <div className={`ai-insight-card ${insight.recommendation}`}>
          <div className="ai-label">
            <span>AI insight</span>
            <span className={`ai-rec ${insight.recommendation}`}>
              {recommendationLabel(insight.recommendation)} · {insight.confidence}
            </span>
          </div>
          <h3>{insight.headline}</h3>
          <ul>
            {(insight.insights || []).map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
          {insight.suggested_change && (
            <p className="suggested">
              <span>What to change to</span>
              {insight.suggested_change}
            </p>
          )}
          {insight.themes?.length > 0 && (
            <p className="suggested">
              <span>Themes</span>
              {insight.themes.join(" · ")}
            </p>
          )}
        </div>
      ) : (
        <div className="ai-empty">
          Paste climber feedback above and run <strong>Analyze with AI</strong>. Insights for this
          route will appear here when you select it.
        </div>
      )}

      {route.holds?.length > 0 && (
        <div className="signal-card" style={{ marginTop: 14 }}>
          <div className="signal-label">
            <span>Hold sequence ({route.holds.length})</span>
          </div>
          <ul style={{ margin: "8px 0 0", paddingLeft: 16, fontSize: 10, color: "#63705f", lineHeight: 1.5 }}>
            {route.holds.map((h) => (
              <li key={`${h.sequence_index}-${h.cell_index}`}>
                #{h.sequence_index + 1} · {h.hold_type} · x {Number(h.x).toFixed(2)}, y{" "}
                {Number(h.y).toFixed(2)} · size {Number(h.size).toFixed(2)}
                {h.notes ? ` · ${h.notes}` : ""}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="signal-card">
        <div className="signal-label">
          <span>Community signal</span>
          <Icon name="info" size={15} />
        </div>
        <div className="rating-line">
          <strong>{route.rating}</strong>
          <span className="stars">★★★★★</span>
          <small>from {route.feedback} responses</small>
        </div>
        <div className="signal-bars">
          <span style={{ width: "72%" }} />
          <span style={{ width: "55%" }} />
          <span style={{ width: "36%" }} />
          <span style={{ width: "14%" }} />
        </div>
        <p>
          {route.status === "Review"
            ? "Perceived difficulty is trending one band harder."
            : route.status === "Strip soon"
              ? "Engagement is fading — candidate for the next reset."
              : "Strong recent engagement with consistent enjoyment."}
        </p>
      </div>
    </aside>
  );
}

export default function App() {
  const [view, setView] = useState("gym");
  const [query, setQuery] = useState("");
  const [filterOpen, setFilterOpen] = useState(false);
  const [selectedId, setSelectedId] = useState(null);
  const [notice, setNotice] = useState("");
  const [feedbackText, setFeedbackText] = useState(SAMPLE_FEEDBACK);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState("");
  const [gymSummary, setGymSummary] = useState("");
  const [insightsById, setInsightsById] = useState({});
  const [provider, setProvider] = useState("");
  const [routeData, setRouteData] = useState([]);
  const [walls, setWalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [addOpen, setAddOpen] = useState(false);
  const [sceneXml, setSceneXml] = useState("");
  const [clearing, setClearing] = useState(false);

  const loadInventory = async () => {
    const [apiWalls, apiRoutes] = await Promise.all([fetchWalls(), fetchRoutes()]);
    setWalls(
      apiWalls.map((w) => ({
        key: w.wall_key || w.angle_type || w.id,
        name: w.name,
        zone: w.zone,
        cols: w.grid_cols || 8,
        rows: w.grid_rows || 10,
        id: w.id,
      })),
    );
    setRouteData(apiRoutes);
    return apiRoutes;
  };

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setLoadError("");
      try {
        const apiRoutes = await loadInventory();
        if (cancelled) return;
        if (apiRoutes.length) {
          setSelectedId((prev) => prev || apiRoutes[0].id);
        } else {
          setSelectedId(null);
        }
      } catch (err) {
        if (!cancelled) setLoadError(err.message || "Failed to load routes");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const selectedRoute = selectedId
    ? routeData.find((route) => route.id === selectedId)
    : null;
  const selectedInsight = selectedRoute ? insightsById[selectedRoute.id] : null;
  const visibleRoutes = useMemo(
    () =>
      routeData.filter((route) =>
        `${route.name} ${route.grade} ${route.wall} ${route.style} ${route.status}`
          .toLowerCase()
          .includes(query.toLowerCase()),
      ),
    [query, routeData],
  );

  const selectRoute = (id) => {
    if (!id) return;
    setSelectedId(id);
    setView("gym");
  };

  const handleRouteCreated = async (batch) => {
    const created = batch.routes || [];
    setSceneXml(batch.xml || "");
    setRouteData((prev) => {
      const ids = new Set(created.map((r) => r.id));
      return [...created, ...prev.filter((r) => !ids.has(r.id))];
    });
    if (created[0]) setSelectedId(created[0].id);
    setAddOpen(false);
    setNotice(
      `Extracted ${batch.total || created.length} routes into scene XML (${batch.provider || "cv"}).`,
    );
    setView("gym");
    try {
      await loadInventory();
      if (created[0]) setSelectedId(created[0].id);
    } catch {
      /* keep optimistic rows */
    }
  };

  const handleClearDemo = async () => {
    if (!window.confirm("Clear all routes for a fresh demo? This cannot be undone.")) return;
    setClearing(true);
    try {
      const result = await clearAllRoutes();
      setRouteData([]);
      setSelectedId(null);
      setSceneXml("");
      setInsightsById({});
      setGymSummary("");
      setNotice(`Demo cleared — removed ${result.deleted ?? 0} routes. Ready for a fresh upload.`);
    } catch (err) {
      setLoadError(err.message || "Clear failed");
    } finally {
      setClearing(false);
    }
  };

  const runAnalyze = async () => {
    setAnalyzing(true);
    setAnalyzeError("");
    try {
      const result = await analyzeFeedback(feedbackText, routeData);
      const map = {};
      for (const item of result.routes || []) {
        map[item.route_id] = item;
      }
      setInsightsById(map);
      setGymSummary(result.gym_summary || "");
      setProvider(result.provider || "");
      setNotice("AI insights ready — click a route to see keep / change-out guidance.");
    } catch (err) {
      setAnalyzeError(err.message || "Analyze failed");
    } finally {
      setAnalyzing(false);
    }
  };

  const keepCount = Object.values(insightsById).filter((i) => i.recommendation === "keep").length;
  const changeCount = Object.values(insightsById).filter((i) => i.recommendation === "change_out").length;

  return (
    <main className="app-shell">
      <section className="workspace">
        <header className="topbar">
          <div className="brand-inline">
            <span className="brand-mark">C</span>
            <div>
              <strong className="brand-name">crux</strong>
              <span className="brand-gym">Summit Lab · route inventory</span>
            </div>
          </div>
          <div className="top-actions">
            <button
              type="button"
              className="clear-demo"
              onClick={handleClearDemo}
              disabled={clearing || loading}
              title="Wipe all routes for the next demo"
            >
              {clearing ? "Clearing…" : "Clear demo"}
            </button>
            <button className="add-route" onClick={() => setAddOpen(true)}>
              <Icon name="plus" size={17} />
              Add route
            </button>
          </div>
        </header>
        {loading && (
          <div className="notice" role="status">
            Loading routes from API…
          </div>
        )}
        {loadError && (
          <div className="notice" role="alert">
            {loadError}
            <button onClick={() => setLoadError("")}>×</button>
          </div>
        )}
        {notice && (
          <div className="notice" role="status">
            {notice}
            <button onClick={() => setNotice("")}>×</button>
          </div>
        )}

        <div className="page-head">
          <div>
            <p className="eyebrow">ROUTE INVENTORY</p>
            <h1>What’s on the wall</h1>
            <p className="subtitle">
              Upload one wall photo to extract every route into editable scene XML and a cartoon
              board (shapes, colors, positions).
            </p>
          </div>
          <div className="as-of">
            <span className="live-dot" />
            Live from API
          </div>
        </div>

        <div className="metric-row">
          <div className="metric">
            <span>Active routes</span>
            <strong>{routeData.length}</strong>
            <small>
              <em>{routeData.length ? "from API" : "none yet"}</em>
            </small>
          </div>
          <div className="metric">
            <span>Change out</span>
            <strong>{changeCount || routeData.filter((r) => r.status === "Review").length || "—"}</strong>
            <small>
              <em className="warn">{changeCount ? "from AI" : "run analyze"}</em>
            </small>
          </div>
          <div className="metric">
            <span>Keep</span>
            <strong>{keepCount || "—"}</strong>
            <small>
              <em>{keepCount ? "AI keepers" : "run analyze"}</em>
            </small>
          </div>
          <div className="coverage-note">
            <span className="coverage-icon">
              <Icon name="chart" />
            </span>
            <div>
              <strong>{gymSummary ? "AI gym summary ready" : "Paste feedback to generate insights"}</strong>
              <small>{provider ? `Provider: ${provider}` : `API: ${API_BASE}`}</small>
            </div>
          </div>
        </div>

        <section className="feedback-lab" aria-label="Climber feedback for AI">
          <div className="feedback-lab-head">
            <div>
              <h2>Climber feedback → AI insights</h2>
              <p>
                Paste survey comments or floor notes. The model maps them onto your saved routes and
                recommends what to keep, what to strip, and what to set next.
              </p>
            </div>
          </div>
          <textarea
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            placeholder="Paste climber feedback here…"
            aria-label="Climber feedback"
          />
          <div className="feedback-lab-actions">
            <button
              className="primary"
              type="button"
              disabled={analyzing || !routeData.length}
              onClick={runAnalyze}
            >
              {analyzing ? "Analyzing…" : "Analyze with AI"}
            </button>
            <button className="ghost" type="button" onClick={() => setFeedbackText(SAMPLE_FEEDBACK)}>
              Load sample feedback
            </button>
            <span className={`feedback-lab-meta ${analyzeError ? "error" : ""}`}>
              {analyzeError ||
                (!routeData.length
                  ? "Add a route first"
                  : Object.keys(insightsById).length
                    ? `${Object.keys(insightsById).length} routes scored`
                    : "Waiting for analysis")}
            </span>
          </div>
          {gymSummary && (
            <div className="gym-summary">
              <strong>Gym priorities</strong>
              {gymSummary}
            </div>
          )}
        </section>

        <div className="content-card">
          <div className="card-toolbar">
            <div className="view-toggle" role="group" aria-label="Choose display">
              <button className={view === "routes" ? "on" : ""} onClick={() => setView("routes")}>
                <Icon name="routes" size={16} />
                Route list
              </button>
              <button className={view === "gym" ? "on" : ""} onClick={() => setView("gym")}>
                <Icon name="map" size={16} />
                Gym view
              </button>
            </div>
            <div className="toolbar-actions">
              <label className="search">
                <Icon name="search" size={17} />
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Search routes"
                />
              </label>
              <button
                className={`filter-button ${filterOpen ? "open" : ""}`}
                onClick={() => setFilterOpen(!filterOpen)}
              >
                <Icon name="filter" size={16} />
                Filters <span>3</span>
              </button>
            </div>
          </div>
          {filterOpen && (
            <div className="filter-popover">
              <button onClick={() => setQuery("V1")}>V1–V2</button>
              <button onClick={() => setQuery("Slab")}>Slab</button>
              <button onClick={() => setQuery("Review")}>Needs review</button>
              <button onClick={() => setQuery("")}>Clear filters</button>
            </div>
          )}
          {!loading && !routeData.length ? (
            <div className="inventory-empty">
              <h3>No routes yet</h3>
              <p>Upload a wall photo — all colored routes are detected into scene XML automatically.</p>
              <button type="button" className="add-route" onClick={() => setAddOpen(true)}>
                <Icon name="plus" size={17} />
                Extract from photo
              </button>
            </div>
          ) : (
            <div className={`view-stage ${view}`}>
              <div className="route-list-panel">
                <div className="list-summary">
                  <strong>{visibleRoutes.length} active routes</strong>
                  <span>
                    Sorted by set date <Icon name="chevron" size={14} />
                  </span>
                </div>
                <div className="route-list">
                  {visibleRoutes.length ? (
                    visibleRoutes.map((route) => (
                      <RouteCard
                        key={route.id}
                        route={route}
                        selected={selectedId === route.id}
                        onClick={selectRoute}
                        insight={insightsById[route.id]}
                      />
                    ))
                  ) : (
                    <div className="empty-state">No routes match that search.</div>
                  )}
                </div>
              </div>
              <GymHoldView
                routes={visibleRoutes.length ? visibleRoutes : routeData}
                walls={walls}
                selected={selectedId}
                selectRoute={selectRoute}
                sceneXml={sceneXml}
              />
              {selectedRoute ? (
                <RouteDetails route={selectedRoute} insight={selectedInsight} />
              ) : (
                <aside className="route-details">
                  <div className="ai-empty">Select a route to inspect holds and AI insights.</div>
                </aside>
              )}
            </div>
          )}
        </div>
        <footer>Summit Lab · Add route from photo · {API_BASE}</footer>
      </section>

      {addOpen && (
        <AddRouteModal
          walls={walls}
          onClose={() => setAddOpen(false)}
          onCreated={handleRouteCreated}
        />
      )}
    </main>
  );
}
