import { useMemo, useState } from "react";
import { HoldGrid } from "./components/HoldGrid";
import "./styles.css";
import "./hold-board.css";

const routeData = [
  {
    id: "r-101",
    name: "Soft Landing",
    identifier: "Green holds",
    grade: "V1",
    wall: "Slab Wall",
    wallKey: "slab",
    zone: "Front",
    setter: "Jordan Setter",
    set: "Jun 28",
    age: "20d",
    style: "Slab",
    rating: 4.4,
    feedback: 22,
    status: "Healthy",
    color: "#3dba6e",
    colorName: "Green",
    cells: [75, 67, 59, 51, 44, 36, 28, 20],
  },
  {
    id: "r-102",
    name: "Reach Check",
    identifier: "Yellow holds",
    grade: "V3",
    wall: "Slab Wall",
    wallKey: "slab",
    zone: "Front",
    setter: "Jordan Setter",
    set: "Jul 13",
    age: "5d",
    style: "Technical",
    rating: 3.8,
    feedback: 14,
    status: "Review",
    color: "#e8c84a",
    colorName: "Yellow",
    cells: [72, 65, 57, 50, 42, 34, 27, 19, 11],
  },
  {
    id: "r-103",
    name: "Cave Crusher",
    identifier: "Red holds",
    grade: "V5",
    wall: "Steep Wall",
    wallKey: "steep",
    zone: "Cave",
    setter: "Sam Setter",
    set: "Jun 13",
    age: "35d",
    style: "Powerful",
    rating: 3.6,
    feedback: 41,
    status: "Review",
    color: "#e24b4b",
    colorName: "Red",
    cells: [73, 66, 58, 49, 41, 33, 25, 17, 10],
  },
  {
    id: "r-104",
    name: "Blue Hour",
    identifier: "Blue holds",
    grade: "V7",
    wall: "Steep Wall",
    wallKey: "steep",
    zone: "Cave",
    setter: "Sam Setter",
    set: "Jul 6",
    age: "12d",
    style: "Coordination",
    rating: 4.6,
    feedback: 19,
    status: "Healthy",
    color: "#3b82f6",
    colorName: "Blue",
    cells: [76, 68, 60, 53, 45, 37, 29, 21, 13],
  },
  {
    id: "r-105",
    name: "Board Meeting",
    identifier: "Orange holds",
    grade: "V2",
    wall: "Vertical Board",
    wallKey: "vertical",
    zone: "Training",
    setter: "Alex Manager",
    set: "Jul 10",
    age: "8d",
    style: "Fun",
    rating: 4.7,
    feedback: 27,
    status: "Healthy",
    color: "#f07a2a",
    colorName: "Orange",
    cells: [77, 69, 61, 52, 44, 36, 28, 20, 12],
  },
  {
    id: "r-106",
    name: "Purple Rain",
    identifier: "Purple holds",
    grade: "V4",
    wall: "Vertical Board",
    wallKey: "vertical",
    zone: "Training",
    setter: "Jordan Setter",
    set: "Jun 3",
    age: "45d",
    style: "Compression",
    rating: 3.9,
    feedback: 32,
    status: "Strip soon",
    color: "#9b6bff",
    colorName: "Purple",
    cells: [74, 66, 58, 50, 43, 35, 27, 18],
  },
];

const initials = (name) =>
  name
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

function RouteCard({ route, selected, onClick }) {
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
      <span className={`route-status ${route.status.toLowerCase().replace(" ", "-")}`}>{route.status}</span>
      <Icon name="chevron" size={15} />
    </button>
  );
}

function GymHoldView({ routes, selected, selectRoute }) {
  const selectedRoute = routes.find((r) => r.id === selected);
  const wallKey = selectedRoute?.wallKey ?? "slab";

  return (
    <section className="gym-map gym-hold-view" aria-label="Lit hold boards">
      <div className="map-heading">
        <span>Hold boards</span>
        <small>Active routes light the grid — tap a hold to inspect</small>
      </div>
      <HoldGrid
        routes={routes}
        selectedWallKey={wallKey}
        selectedRouteId={selected}
        onSelectWall={() => {}}
        onSelectRoute={selectRoute}
      />
    </section>
  );
}

function RouteDetails({ route }) {
  return (
    <aside className="route-details">
      <div className="detail-topline">
        <span className={`route-status ${route.status.toLowerCase().replace(" ", "-")}`}>{route.status}</span>
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
          <span>{route.cells.length}</span>
        </div>
      </div>
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
      <button className="outline-action">
        Open route details <Icon name="arrow" size={16} />
      </button>
    </aside>
  );
}

export default function App() {
  const [view, setView] = useState("gym");
  const [query, setQuery] = useState("");
  const [filterOpen, setFilterOpen] = useState(false);
  const [selectedId, setSelectedId] = useState("r-102");
  const [notice, setNotice] = useState("");

  const selectedRoute = routeData.find((route) => route.id === selectedId) ?? routeData[0];
  const visibleRoutes = useMemo(
    () =>
      routeData.filter((route) =>
        `${route.name} ${route.grade} ${route.wall} ${route.style} ${route.status}`
          .toLowerCase()
          .includes(query.toLowerCase()),
      ),
    [query],
  );

  const selectRoute = (id) => {
    if (!id) return;
    setSelectedId(id);
    setView("gym");
  };

  const addRoute = () => setNotice("Route creation will connect to the backend next.");

  return (
    <main className="app-shell">
      <nav className="sidebar">
        <div className="brand">
          <span className="brand-mark">C</span>
          <span>crux</span>
        </div>
        <div className="gym-switch">
          <span className="gym-icon">⌂</span>
          <span>
            <strong>Summit Lab</strong>
            <small>Demo gym</small>
          </span>
          <Icon name="chevron" size={16} />
        </div>
        <div className="nav-section">
          <small>WORKSPACE</small>
          <button className="nav-item active">
            <Icon name="grid" />
            Overview
          </button>
          <button className="nav-item">
            <Icon name="routes" />
            Routes <span className="count">{routeData.length}</span>
          </button>
          <button className="nav-item">
            <Icon name="map" />
            Plan
          </button>
          <button className="nav-item">
            <Icon name="chart" />
            Insights
          </button>
        </div>
        <div className="sidebar-bottom">
          <button className="nav-item">
            <Icon name="settings" />
            Settings
          </button>
          <div className="user">
            <span className="avatar">MC</span>
            <span>
              <strong>Maya Chen</strong>
              <small>Setting manager</small>
            </span>
            <Icon name="dots" size={17} />
          </div>
        </div>
      </nav>

      <section className="workspace">
        <header className="topbar">
          <div className="crumb">
            <span>Overview</span>
            <Icon name="chevron" size={14} />
            <strong>Active routes</strong>
          </div>
          <div className="top-actions">
            <button className="icon-button notification">
              <Icon name="bell" />
              <b />
            </button>
            <button className="add-route" onClick={addRoute}>
              <Icon name="plus" size={17} />
              Add route
            </button>
          </div>
        </header>
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
            <p className="subtitle">Staff dashboard with lit hold boards for each active route.</p>
          </div>
          <div className="as-of">
            <span className="live-dot" />
            Updated just now
          </div>
        </div>

        <div className="metric-row">
          <div className="metric">
            <span>Active routes</span>
            <strong>{routeData.length}</strong>
            <small>
              <em>+2</em> this cycle
            </small>
          </div>
          <div className="metric">
            <span>Need review</span>
            <strong>{routeData.filter((r) => r.status === "Review").length}</strong>
            <small>
              <em className="warn">sharp / sandbag</em>
            </small>
          </div>
          <div className="metric">
            <span>Feedback this week</span>
            <strong>{routeData.reduce((n, r) => n + r.feedback, 0)}</strong>
            <small>
              <em>+12%</em> from last week
            </small>
          </div>
          <div className="coverage-note">
            <span className="coverage-icon">
              <Icon name="map" />
            </span>
            <div>
              <strong>Coverage gap: easy slab</strong>
              <small>Only one V1 on Slab Wall</small>
            </div>
            <button>
              View plan <Icon name="arrow" size={15} />
            </button>
          </div>
        </div>

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
                    />
                  ))
                ) : (
                  <div className="empty-state">No routes match that search.</div>
                )}
              </div>
            </div>
            <GymHoldView
              routes={visibleRoutes.length ? visibleRoutes : routeData}
              selected={selectedId}
              selectRoute={selectRoute}
            />
            <RouteDetails route={selectedRoute} />
          </div>
        </div>
        <footer>Summit Lab · Staff workspace · Hold boards wired to route inventory</footer>
      </section>
    </main>
  );
}
