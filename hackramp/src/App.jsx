style: 'Endurance',
rating: 3.9,
feedback: 32,
status: 'Review',
color: '#b28bff',
position: { left: '78%', top: '28%' },
},
{
id: 'r-108',
name: 'Small Victories',
identifier: 'Yellow holds',
grade: 'V0',
wall: 'Front Slab',
zone: 'North floor',
setter: 'Ari Moore',
set: 'Jun 23',
age: '25d',
style: 'Balance',
rating: 4.5,
feedback: 18,
status: 'Strip soon',
color: '#f8df4b',
position: { left: '29%', top: '40%' },
},
{
id: 'r-109',
name: 'Side Quest',
identifier: 'Red holds',
grade: 'V5',
wall: 'Cave',
zone: 'West wall',
setter: 'Theo James',
set: 'Jun 20',
age: '28d',
style: 'Compression',
rating: 4.2,
feedback: 26,
status: 'Healthy',
color: '#ec5c66',
position: { left: '61%', top: '63%' },
},
]

const initials = (name) => name.split(' ').map((part) => part[0]).join('')

function Icon({ name, size = 18, stroke = 1.8 }) {
const paths = {
grid: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>,
routes: <><path d="M5 4h14" /><path d="M5 10h14" /><path d="M5 16h10" /><circle cx="3" cy="4" r=".7" fill="currentColor" /><circle cx="3" cy="10" r=".7" fill="currentColor" /><circle cx="3" cy="16" r=".7" fill="currentColor" /></>,
map: <><path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z" /><path d="M9 3v15M15 6v15" /></>,
chart: <><path d="M4 19V5" /><path d="M4 19h16" /><path d="m7 15 4-5 3 2 5-7" /></>,
settings: <><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.12 2.12-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V20.3h-3v-.08A1.7 1.7 0 0 0 10.68 18.66a1.7 1.7 0 0 0-1.88.34l-.06.06-2.12-2.12.06-.06A1.7 1.7 0 0 0 7.02 15a1.7 1.7 0 0 0-1.56-1.03H5.4v-3h.08A1.7 1.7 0 0 0 7.02 9.94a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.12-2.12.06.06a1.7 1.7 0 0 0 1.88.34 1.7 1.7 0 0 0 1.03-1.56V4.64h3v.08a1.7 1.7 0 0 0 1.03 1.56 1.7 1.7 0 0 0 1.88-.34l.06-.06 2.12 2.12-.06.06a1.7 1.7 0 0 0-.34 1.88 1.7 1.7 0 0 0 1.56 1.03h.08v3h-.08A1.7 1.7 0 0 0 19.4 15Z" /></>,
search: <><circle cx="10.8" cy="10.8" r="6.2" /><path d="m16 16 4 4" /></>,
chevron: <path d="m9 18 6-6-6-6" />,
plus: <><path d="M12 5v14" /><path d="M5 12h14" /></>,
filter: <><path d="M4 6h16" /><path d="M7 12h10" /><path d="M10 18h4" /></>,
bell: <><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" /><path d="M10 21h4" /></>,
dots: <><circle cx="5" cy="12" r="1.25" fill="currentColor" /><circle cx="12" cy="12" r="1.25" fill="currentColor" /><circle cx="19" cy="12" r="1.25" fill="currentColor" /></>,
arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
info: <><circle cx="12" cy="12" r="9" /><path d="M12 11v5" /><path d="M12 8h.01" /></>,
calendar: <><rect x="3.5" y="5" width="17" height="15.5" rx="2" /><path d="M7.5 3v4M16.5 3v4M3.5 10h17" /></>,
}
return <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>
}

function RouteCard({ route, selected, onClick }) {
return (
<button className={`route-card ${selected ? 'selected' : ''}`} onClick={() => onClick(route.id)}>
  <span className="route-swatch" style={{ background: route.color }} />
  <span className="route-main">
    <span className="route-name-line"><strong>{route.name}</strong><span className="grade">{route.grade}</span></span>
    <span className="route-meta">{route.wall} · {route.style}</span>
  </span>
  <span className={`route-status ${route.status.toLowerCase().replace(' ', '-')}`}>{route.status}</span>
  <Icon name="chevron" size={15} />
</button>
)
}

function GymMap({ routes, selected, selectRoute }) {
return (
<section className="gym-map" aria-label="Top view of the gym">
  <div className="map-heading"><span>Top view</span><small>Tap a route to inspect</small></div>
  <div className="floor-plan">
    <div className="map-rug rug-a" />
    <div className="map-rug rug-b" />
    <div className="wall slab-wall"><span>Front slab</span><i /></div>
    <div className="wall overhang-wall"><span>Overhang</span><i /></div>
    <div className="wall cave-wall"><span>Cave</span><i /></div>
    <div className="wall training-wall"><span>Training wall</span><i /></div>
    <div className="desk"><span>Check-in</span></div>
    <div className="bench bench-one" />
    <div className="bench bench-two" />
    <div className="map-entry">Entrance</div>
    {routes.map((route) => (
      <button
        key={route.id}
        className={`map-route ${selected === route.id ? 'active' : ''}`}
        style={{ ...route.position, '--route-color': route.color }}
        onClick={() => selectRoute(route.id)}
        aria-label={`${route.name}, ${route.grade}, ${route.wall}`}
      >
        <span>{route.grade}</span>
      </button>
    ))}
    <div className="map-north">N <span>↑</span></div>
  </div>
</section>
)
}

function RouteDetails({ route }) {
return (
<aside className="route-details">
  <div className="detail-topline"><span className={`route-status ${route.status.toLowerCase().replace(' ', '-')}`}>{route.status}</span><button aria-label="More actions" className="icon-button"><Icon name="dots" /></button></div>
  <div className="detail-route-title"><span className="large-swatch" style={{ background: route.color }} /><div><h2>{route.name}</h2><p>{route.identifier} · {route.grade}</p></div></div>
  <div className="detail-location"><Icon name="map" size={16} /><span>{route.wall}, {route.zone}</span></div>
  <div className="details-grid">
    <div><small>Setter</small><span><b className="avatar mini">{initials(route.setter)}</b>{route.setter}</span></div>
    <div><small>Set date</small><span><Icon name="calendar" size={15} />{route.set}</span></div>
    <div><small>On wall</small><span>{route.age}</span></div>
    <div><small>Style</small><span>{route.style}</span></div>
  </div>
  <div className="signal-card">
    <div className="signal-label"><span>Community signal</span><Icon name="info" size={15} /></div>
    <div className="rating-line"><strong>{route.rating}</strong><span className="stars">★★★★★</span><small>from {route.feedback} responses</small></div>
    <div className="signal-bars"><span style={{ width: '72%' }} /><span style={{ width: '55%' }} /><span style={{ width: '36%' }} /><span style={{ width: '14%' }} /></div>
    <p>{route.status === 'Review' ? 'Perceived difficulty is trending one band harder.' : 'Strong recent engagement with consistent enjoyment.'}</p>
  </div>
  <button className="outline-action">Open route details <Icon name="arrow" size={16} /></button>
</aside>
)
}

function App() {
const [view, setView] = useState('routes')
const [query, setQuery] = useState('')
const [filterOpen, setFilterOpen] = useState(false)
const [selectedId, setSelectedId] = useState('r-105')
const [notice, setNotice] = useState('')
const selectedRoute = routeData.find((route) => route.id === selectedId) ?? routeData[0]
const visibleRoutes = useMemo(() => routeData.filter((route) => (`${route.name} ${route.grade} ${route.wall} ${route.style}`).toLowerCase().includes(query.toLowerCase())), [query])
const selectRoute = (id) => {
setSelectedId(id)
setView('gym')
}
const addRoute = () => setNotice('Route creation will connect to the backend next.')

return (
<main className="app-shell">
  <nav className="sidebar">
    <div className="brand"><span className="brand-mark">C</span><span>crux</span></div>
    <div className="gym-switch"><span className="gym-icon">⌂</span><span><strong>Rockhaven</strong><small>Brooklyn, NY</small></span><Icon name="chevron" size={16} /></div>
    <div className="nav-section"><small>WORKSPACE</small>
      <button className="nav-item active"><Icon name="grid" />Overview</button>
      <button className="nav-item"><Icon name="routes" />Routes <span className="count">68</span></button>
      <button className="nav-item"><Icon name="map" />Plan</button>
      <button className="nav-item"><Icon name="chart" />Insights</button>
    </div>
    <div className="sidebar-bottom"><button className="nav-item"><Icon name="settings" />Settings</button><div className="user"><span className="avatar">MC</span><span><strong>Maya Chen</strong><small>Setting manager</small></span><Icon name="dots" size={17} /></div></div>
  </nav>

  <section className="workspace">
    <header className="topbar"><div className="crumb"><span>Overview</span><Icon name="chevron" size={14} /><strong>Active routes</strong></div><div className="top-actions"><button className="icon-button notification"><Icon name="bell" /><b /></button><button className="add-route" onClick={addRoute}><Icon name="plus" size={17} />Add route</button></div></header>
    {notice && <div className="notice" role="status">{notice}<button onClick={() => setNotice('')}>×</button></div>}

    <div className="page-head"><div><p className="eyebrow">ROUTE INVENTORY</p><h1>What’s on the wall</h1><p className="subtitle">Current routes across Rockhaven, with the signals that matter.</p></div><div className="as-of"><span className="live-dot" />Updated just now</div></div>
    <div className="metric-row"><div className="metric"><span>Active routes</span><strong>68</strong><small><em>+6</em> this cycle</small></div><div className="metric"><span>Need review</span><strong>7</strong><small><em className="warn">3</em> need attention</small></div><div className="metric"><span>Feedback this week</span><strong>184</strong><small><em>+22%</em> from last week</small></div><div className="coverage-note"><span className="coverage-icon"><Icon name="map" /></span><div><strong>Coverage gap: V1–V2 slab</strong><small>2 routes below your target range</small></div><button>View plan <Icon name="arrow" size={15} /></button></div></div>

    <div className="content-card">
      <div className="card-toolbar"><div className="view-toggle" role="group" aria-label="Choose display"><button className={view === 'routes' ? 'on' : ''} onClick={() => setView('routes')}><Icon name="routes" size={16} />Route list</button><button className={view === 'gym' ? 'on' : ''} onClick={() => setView('gym')}><Icon name="map" size={16} />Gym view</button></div><div className="toolbar-actions"><label className="search"><Icon name="search" size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search routes" /></label><button className={`filter-button ${filterOpen ? 'open' : ''}`} onClick={() => setFilterOpen(!filterOpen)}><Icon name="filter" size={16} />Filters <span>3</span></button></div></div>
      {filterOpen && <div className="filter-popover"><button onClick={() => setQuery('V1')}>V1–V2</button><button onClick={() => setQuery('Slab')}>Slab</button><button onClick={() => setQuery('Review')}>Needs review</button><button onClick={() => setQuery('')}>Clear filters</button></div>}
      <div className={`view-stage ${view}`}>
        <div className="route-list-panel">
          <div className="list-summary"><strong>{visibleRoutes.length} active routes</strong><span>Sorted by set date <Icon name="chevron" size={14} /></span></div>
          <div className="route-list">{visibleRoutes.length ? visibleRoutes.map((route) => <RouteCard key={route.id} route={route} selected={selectedId === route.id} onClick={selectRoute} />) : <div className="empty-state">No routes match that search.</div>}</div>
        </div>
        <GymMap routes={visibleRoutes.length ? visibleRoutes : routeData} selected={selectedId} selectRoute={selectRoute} />
        <RouteDetails route={selectedRoute} />
      </div>
    </div>
    <footer>Rockhaven climbing · Staff workspace · Demo data</footer>
  </section>
</main>
)
}

export default App