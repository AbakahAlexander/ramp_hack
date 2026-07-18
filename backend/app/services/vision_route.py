"""Vision: photo of a climb → normalized hold grid for the wall."""

from __future__ import annotations

import base64
import json
import re
from typing import Any

from openai import OpenAI

from app.config import get_settings

VISION_SYSTEM = """You are Crux, a climbing routesetting assistant.
You receive a photo of an indoor climbing route (holds of one color on a wall).
Map the climb onto a normalized rectangular grid for that wall.

Return ONLY valid JSON:
{
  "name": "short route name",
  "color_identifier": "primary hold color name e.g. Yellow",
  "display_color": "#RRGGBB approximate hex for that color",
  "assigned_grade": "best guess V-scale e.g. V3 or V?",
  "styles": ["slab"|"technical"|"powerful"|...],
  "holds": [
    {
      "sequence_index": 0,
      "row": 0,
      "col": 0,
      "hold_type": "jug"|"crimp"|"pinch"|"sloper"|"foothold"|"volume"|"pocket"|"other",
      "notes": "start|crux|finish|null"
    }
  ],
  "notes": "optional setter note"
}

Rules:
- Grid is row-major: row 0 is TOP of the wall, col 0 is LEFT.
- grid_cols and grid_rows are given — every hold row/col must be inside [0, rows) and [0, cols).
- sequence_index 0 is the start (usually lowest holds); increase toward the top/finish.
- Include only holds that belong to THIS route (same color / tape), not other routes.
- Prefer 5–14 holds. Estimate hold_type from shape when possible.
- If grade is unclear use "V?".
"""


def _client() -> OpenAI | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    return OpenAI(api_key=settings.openai_api_key)


def _fallback_from_image(grid_cols: int, grid_rows: int, color_hint: str | None) -> dict[str, Any]:
    """Deterministic diagonal when no API key — still creates a valid grid route."""
    color = color_hint or "Teal"
    hex_map = {
        "yellow": "#e8c84a",
        "green": "#3dba6e",
        "red": "#e24b4b",
        "blue": "#3b82f6",
        "purple": "#9b6bff",
        "orange": "#f07a2a",
        "teal": "#14b8a6",
    }
    display = hex_map.get(color.lower(), "#14b8a6")
    holds = []
    # climb from bottom-left toward top-center
    path = []
    for i in range(min(8, grid_rows)):
        row = grid_rows - 1 - i
        col = min(i, grid_cols - 1)
        path.append((row, col))
    types = ["jug", "crimp", "pinch", "sloper", "crimp", "pinch", "volume", "jug"]
    for i, (row, col) in enumerate(path):
        holds.append(
            {
                "sequence_index": i,
                "row": row,
                "col": col,
                "hold_type": types[i % len(types)],
                "notes": "start" if i == 0 else ("finish" if i == len(path) - 1 else None),
            }
        )
    return {
        "name": f"{color} AI Route",
        "color_identifier": color,
        "display_color": display,
        "assigned_grade": "V?",
        "styles": ["technical"],
        "holds": holds,
        "notes": "Generated without OpenAI (fallback diagonal). Set OPENAI_API_KEY for vision.",
        "provider": "fallback",
    }


def extract_route_from_image(
    image_bytes: bytes,
    content_type: str,
    grid_cols: int,
    grid_rows: int,
    *,
    color_hint: str | None = None,
    wall_name: str | None = None,
) -> dict[str, Any]:
    client = _client()
    if client is None:
        return _fallback_from_image(grid_cols, grid_rows, color_hint)

    settings = get_settings()
    mime = content_type if content_type in ("image/jpeg", "image/png", "image/webp", "image/gif") else "image/jpeg"
    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime};base64,{b64}"

    user_text = (
        f"Wall grid is {grid_cols} columns × {grid_rows} rows "
        f"(row 0 = top, col 0 = left)."
    )
    if wall_name:
        user_text += f" Wall name: {wall_name}."
    if color_hint:
        user_text += f" Route color hint: {color_hint}."
    user_text += " Extract the route into JSON."

    # Prefer a vision-capable model; allow override via OPENAI_MODEL
    model = settings.openai_model
    if "mini" in model and "4o" not in model:
        model = "gpt-4o-mini"

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": VISION_SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
    )
    raw = response.choices[0].message.content or "{}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group(0)) if match else {}

    holds_in = data.get("holds") or []
    normalized = []
    for i, h in enumerate(holds_in):
        row = int(h.get("row", 0))
        col = int(h.get("col", 0))
        row = max(0, min(grid_rows - 1, row))
        col = max(0, min(grid_cols - 1, col))
        ht = h.get("hold_type") or "other"
        if ht not in ("jug", "crimp", "pinch", "sloper", "foothold", "volume", "pocket", "other"):
            ht = "other"
        normalized.append(
            {
                "sequence_index": int(h.get("sequence_index", i)),
                "row": row,
                "col": col,
                "hold_type": ht,
                "notes": h.get("notes"),
            }
        )
    if not normalized:
        return _fallback_from_image(grid_cols, grid_rows, color_hint or data.get("color_identifier"))

    normalized.sort(key=lambda x: x["sequence_index"])
    for i, h in enumerate(normalized):
        h["sequence_index"] = i

    return {
        "name": data.get("name") or f"{data.get('color_identifier') or color_hint or 'New'} Route",
        "color_identifier": data.get("color_identifier") or color_hint or "Mixed",
        "display_color": data.get("display_color") or "#888888",
        "assigned_grade": data.get("assigned_grade") or "V?",
        "styles": data.get("styles") if isinstance(data.get("styles"), list) else ["technical"],
        "holds": normalized,
        "notes": data.get("notes"),
        "provider": "openai",
        "model": model,
    }
