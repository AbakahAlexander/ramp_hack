export const API_BASE =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") ||
  "https://holy-merrill-tormame-aafedec0.koyeb.app";

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
