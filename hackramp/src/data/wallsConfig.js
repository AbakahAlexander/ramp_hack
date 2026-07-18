export const WALLS = [
  { key: "slab", name: "Slab Wall", zone: "Front", cols: 8, rows: 10 },
  { key: "steep", name: "Steep Wall", zone: "Cave", cols: 8, rows: 10 },
  { key: "vertical", name: "Vertical Board", zone: "Training", cols: 8, rows: 10 },
];

export function isLitStatus(status) {
  return status === "Healthy" || status === "Review" || status === "active" || status === "needs_review";
}
