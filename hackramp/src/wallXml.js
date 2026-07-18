/** Build / parse Crux wall scene XML in the browser (optimize by editing XML). */

const SHAPE_BY_TYPE = {
  volume: "triangle",
  jug: "rounded_rect",
  pinch: "oval",
  sloper: "oval",
  crimp: "circle",
  foothold: "circle",
  pocket: "circle",
  other: "polygon",
};

export function holdShape(type) {
  return SHAPE_BY_TYPE[(type || "other").toLowerCase()] || "circle";
}

/** Build <wall> XML from dashboard routes (0–1 holds → 0–100 viewBox). */
export function buildWallXml(routes, { wallName = "Wall", wallId = "" } = {}) {
  const routeXml = (routes || [])
    .map((r) => {
      const holds = (r.holds || [])
        .map((h) => {
          const size = Number(h.size) || 0.05;
          const wh = Math.max(1.5, Math.min(18, size * 55));
          const shape = h.shape || holdShape(h.hold_type);
          const notes = h.notes ? ` notes="${escapeXml(h.notes)}"` : "";
          return `    <hold seq="${h.sequence_index ?? 0}" x="${(Number(h.x) * 100).toFixed(2)}" y="${(Number(h.y) * 100).toFixed(2)}" w="${wh.toFixed(2)}" h="${wh.toFixed(2)}" shape="${shape}" type="${h.hold_type || "other}"${notes}/>`;
        })
        .join("\n");
      return `  <route id="${escapeXml(r.id || "")}" name="${escapeXml(r.name || r.colorName || "Route")}" color="${escapeXml(r.colorName || r.color_identifier || "")}" hex="${escapeXml(r.color || "#888")}" grade="${escapeXml(r.grade || "V?")}">\n${holds}\n  </route>`;
    })
    .join("\n");
  return `<?xml version="1.0"?>\n<wall name="${escapeXml(wallName)}" id="${escapeXml(wallId)}" viewBox="0 0 100 100">\n${routeXml}\n</wall>\n`;
}

export function parseWallXml(xmlText) {
  const doc = new DOMParser().parseFromString(xmlText, "application/xml");
  if (doc.querySelector("parsererror")) throw new Error("Invalid wall XML");
  const wall = doc.querySelector("wall");
  if (!wall) throw new Error("Root <wall> missing");
  const routes = [...wall.querySelectorAll("route")].map((rEl) => {
    const holds = [...rEl.querySelectorAll("hold")].map((hEl) => {
      const w = parseFloat(hEl.getAttribute("w") || "5");
      const h = parseFloat(hEl.getAttribute("h") || "5");
      return {
        sequence_index: parseInt(hEl.getAttribute("seq") || "0", 10),
        x: parseFloat(hEl.getAttribute("x") || "50") / 100,
        y: parseFloat(hEl.getAttribute("y") || "50") / 100,
        size: Math.max(w, h) / 55,
        hold_type: hEl.getAttribute("type") || "other",
        shape: hEl.getAttribute("shape") || holdShape(hEl.getAttribute("type")),
        notes: hEl.getAttribute("notes"),
      };
    });
    holds.sort((a, b) => a.sequence_index - b.sequence_index);
    return {
      id: rEl.getAttribute("id") || undefined,
      name: rEl.getAttribute("name") || "Route",
      colorName: rEl.getAttribute("color") || "Mixed",
      color: rEl.getAttribute("hex") || "#888888",
      grade: rEl.getAttribute("grade") || "V?",
      holds,
    };
  });
  return {
    wallName: wall.getAttribute("name") || "Wall",
    wallId: wall.getAttribute("id") || null,
    routes,
  };
}

function escapeXml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
