export const API_BASE =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") ||
  "https://holy-merrill-tormame-aafedec0.koyeb.app";

const STATUS_LABEL = {
  active: "Healthy",
  needs_review: "Review",
  scheduled_for_strip: "Strip soon",
  archived: "Archived",
};

/** Map API route → dashboard / HoldGrid shape */
export function mapApiRoute(r) {
  const setDate = r.set_date ? new Date(r.set_date) : null;
  const ageDays = r.health?.age_days ?? (setDate ? Math.floor((Date.now() - setDate) / 86400000) : 0);
  return {
    id: r.id,
    name: r.name || r.color_identifier,
    identifier: `${r.color_identifier} holds`,
    grade: r.assigned_grade,
    wall: r.wall_name || "",
    wallKey: r.wall_key || "slab",
    wallId: r.wall_id,
    zone: r.zone || "",
    setter: r.setters?.[0]?.full_name || "Unknown",
    set: setDate
      ? setDate.toLocaleDateString("en-US", { month: "short", day: "numeric" })
      : "",
    age: `${ageDays}d`,
    style: (r.styles && r.styles[0]) || "",
    styles: r.styles || [],
    rating: r.health?.enjoyment_avg ?? 0,
    feedback: (r.health?.sends || 0) + (r.health?.attempts || 0) + (r.health?.projects || 0),
    status: STATUS_LABEL[r.status] || r.status,
    apiStatus: r.status,
    color: r.display_color || "#888888",
    colorName: r.color_identifier,
    cells: r.cells?.length ? r.cells : (r.holds || []).map((h) => h.cell_index),
    holds: r.holds || [],
    health: r.health,
    notes: r.notes,
  };
}

export async function fetchWalls() {
  const res = await fetch(`${API_BASE}/api/v1/walls`);
  if (!res.ok) throw new Error(`Failed to load walls (${res.status})`);
  return res.json();
}

export async function fetchRoutes() {
  const res = await fetch(`${API_BASE}/api/v1/routes`);
  if (!res.ok) throw new Error(`Failed to load routes (${res.status})`);
  const body = await res.json();
  return (body.items || []).map(mapApiRoute);
}

export async function createRouteFromImage({ wallId, file, name, color, grade }) {
  const form = new FormData();
  form.append("wall_id", wallId);
  form.append("image", file);
  if (name) form.append("name", name);
  if (color) form.append("color_identifier", color);
  if (grade) form.append("assigned_grade", grade);

  const res = await fetch(`${API_BASE}/api/v1/routes/from-image`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err.detail;
    const msg = Array.isArray(detail)
      ? detail.map((d) => d.msg || JSON.stringify(d)).join("; ")
      : detail || `Upload failed (${res.status})`;
    throw new Error(msg);
  }
  return res.json();
}

export async function analyzeFeedback(feedbackText, routes) {
  const res = await fetch(`${API_BASE}/api/v1/insights/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      feedback_text: feedbackText,
      routes: routes.map((r) => ({
        id: r.id,
        name: r.name,
        grade: r.grade,
        wall: r.wall,
        zone: r.zone,
        style: r.style,
        colorName: r.colorName,
        identifier: r.identifier,
        age: r.age,
        status: r.status,
        setter: r.setter,
      })),
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Analyze failed (${res.status})`);
  }
  return res.json();
}

export const SAMPLE_FEEDBACK = `Yellow V3 on the slab felt super reachy and sandbagged — taller climbers only. A few people said Soft Landing (green V1) is perfect for beginners.

Red cave route has a sharp finishing hold — someone almost cut their finger. Please fix or strip.

Blue V7 is awesome coordination, keep it.

Orange V2 on the board is a blast, classic fun setter piece — keep forever.

Purple board climb is tired and boring after 45 days; strip it and set something more dynamic around V3–V4.`;
