"""Photo of a climb → continuous hold positions (normalized x/y + size).

Prefer classical color segmentation for accuracy on gym photos / illustrations.
OpenAI vision is an optional fallback when CV finds nothing and a key is set.
"""

from __future__ import annotations

import base64
import json
import re
from typing import Any

import cv2
import numpy as np
from openai import OpenAI

from app.config import get_settings

# HSV ranges tuned for the illustrated multi-route wall and typical tape colors.
# OpenCV H is 0–179.
COLOR_HSV: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
    "pink": [((140, 60, 80), (175, 255, 255)), ((0, 60, 80), (8, 255, 255))],
    "magenta": [((140, 60, 80), (175, 255, 255))],
    "red": [((0, 90, 80), (8, 255, 255)), ((170, 90, 80), (179, 255, 255))],
    "orange": [((8, 90, 90), (22, 255, 255))],
    "yellow": [((22, 80, 90), (38, 255, 255))],
    "green": [((38, 60, 60), (90, 255, 255))],
    "teal": [((85, 60, 60), (100, 255, 255))],
    "blue": [((95, 70, 50), (130, 255, 255))],
    "purple": [((125, 50, 50), (150, 255, 255))],
}

DISPLAY_HEX = {
    "pink": "#e85a9b",
    "magenta": "#d946a6",
    "red": "#e24b4b",
    "orange": "#f07a2a",
    "yellow": "#e8c84a",
    "green": "#3dba6e",
    "teal": "#14b8a6",
    "blue": "#3b82f6",
    "purple": "#9b6bff",
}


def _client() -> OpenAI | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    return OpenAI(api_key=settings.openai_api_key)


def _normalize_color_key(hint: str | None) -> str | None:
    if not hint:
        return None
    key = hint.strip().lower()
    aliases = {
        "blu": "blue",
        "yel": "yellow",
        "grn": "green",
        "org": "orange",
        "pnk": "pink",
        "mag": "magenta",
    }
    for name in COLOR_HSV:
        if name in key:
            return name
    for alias, name in aliases.items():
        if alias in key:
            return name
    return None


def _decode_image(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")
    return img


def _mask_for_color(hsv: np.ndarray, color_key: str) -> np.ndarray:
    ranges = COLOR_HSV.get(color_key)
    if not ranges:
        return np.zeros(hsv.shape[:2], dtype=np.uint8)
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lo, hi in ranges:
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv, np.array(lo), np.array(hi)))
    return mask


def _detect_holds_cv(
    img_bgr: np.ndarray,
    color_key: str,
) -> list[dict[str, Any]]:
    """Contours of one route color → normalized x,y,size blobs."""
    h, w = img_bgr.shape[:2]
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = _mask_for_color(hsv, color_key)

    # Soften bolt-hole noise; keep volumes and irregular holds.
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # For blue holds on a blue panel: keep only darker / more saturated blobs.
    if color_key == "blue":
        v = hsv[:, :, 2]
        s = hsv[:, :, 1]
        dark = (v < 200).astype(np.uint8) * 255
        sat = (s > 90).astype(np.uint8) * 255
        mask = cv2.bitwise_and(mask, dark)
        mask = cv2.bitwise_and(mask, sat)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_img = float(h * w)
    min_area = max(40.0, area_img * 0.00012)
    max_area = area_img * 0.08

    holds: list[dict[str, Any]] = []
    for cnt in contours:
        area = float(cv2.contourArea(cnt))
        if area < min_area or area > max_area:
            continue
        m = cv2.moments(cnt)
        if m["m00"] <= 0:
            continue
        cx = m["m10"] / m["m00"]
        cy = m["m01"] / m["m00"]
        # Ignore crash-pad band at the very bottom (~bottom 8%)
        if cy > h * 0.94:
            continue
        (_, _), radius = cv2.minEnclosingCircle(cnt)
        # Normalized: x left→right, y top→bottom; size ≈ relative radius
        nx = float(np.clip(cx / w, 0.0, 1.0))
        ny = float(np.clip(cy / h, 0.0, 1.0))
        nsize = float(np.clip((radius * 2.0) / max(w, h), 0.015, 0.35))

        # Rough type from relative size
        if nsize >= 0.12:
            hold_type = "volume"
        elif nsize >= 0.055:
            hold_type = "jug"
        elif nsize >= 0.035:
            hold_type = "pinch"
        else:
            hold_type = "crimp"

        holds.append(
            {
                "x": round(nx, 4),
                "y": round(ny, 4),
                "size": round(nsize, 4),
                "hold_type": hold_type,
                "area": area,
            }
        )

    # Climb order: bottom → top (start near pads)
    holds.sort(key=lambda hh: (-hh["y"], hh["x"]))
    for i, hh in enumerate(holds):
        hh["sequence_index"] = i
        hh["notes"] = "start" if i == 0 else ("finish" if i == len(holds) - 1 else None)
        hh.pop("area", None)
    return holds


def _guess_dominant_route_color(img_bgr: np.ndarray) -> str:
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    best_key = "blue"
    best_count = 0
    for key in ("pink", "orange", "yellow", "green", "blue", "purple", "red"):
        mask = _mask_for_color(hsv, key)
        if key == "blue":
            v = hsv[:, :, 2]
            mask = cv2.bitwise_and(mask, (v < 200).astype(np.uint8) * 255)
        count = int(cv2.countNonZero(mask))
        if count > best_count:
            best_count = count
            best_key = key
    return best_key


def _legacy_grid_from_spatial(
    holds: list[dict[str, Any]],
    grid_cols: int,
    grid_rows: int,
) -> list[dict[str, Any]]:
    """Derive coarse row/col for older clients; spatial x/y/size remain source of truth."""
    out = []
    for h in holds:
        col = int(np.clip(round(h["x"] * (grid_cols - 1)), 0, grid_cols - 1))
        row = int(np.clip(round(h["y"] * (grid_rows - 1)), 0, grid_rows - 1))
        out.append(
            {
                **h,
                "row": row,
                "col": col,
                "cell_index": row * grid_cols + col,
            }
        )
    return out


def _openai_spatial_extract(
    image_bytes: bytes,
    content_type: str,
    color_hint: str | None,
    wall_name: str | None,
) -> dict[str, Any] | None:
    client = _client()
    if client is None:
        return None

    settings = get_settings()
    mime = content_type if content_type in ("image/jpeg", "image/png", "image/webp", "image/gif") else "image/jpeg"
    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime};base64,{b64}"

    system = """You map ONE climbing route from a wall photo into continuous coordinates.
Return ONLY JSON:
{
  "name": "short name",
  "color_identifier": "Pink|Blue|Green|Yellow|Orange|...",
  "display_color": "#RRGGBB",
  "assigned_grade": "V?" ,
  "styles": ["technical"],
  "holds": [
    {"sequence_index":0,"x":0.12,"y":0.88,"size":0.06,"hold_type":"jug","notes":"start"}
  ],
  "notes": null
}
Rules:
- x,y are normalized 0..1 (x=0 left, y=0 top of the wall image).
- size is relative diameter 0.02..0.30 (volumes large, crimps small).
- Include ONLY holds of the target route color — not other routes.
- Prefer 6–20 holds. sequence_index 0 = start near bottom (high y), finish near top (low y).
- Do NOT snap to a grid. Place centers where the holds actually are.
"""
    user = "Extract the route as continuous holds."
    if color_hint:
        user += f" Target color: {color_hint}."
    if wall_name:
        user += f" Wall: {wall_name}."

    model = settings.openai_model
    if "mini" in model and "4o" not in model:
        model = "gpt-4o-mini"

    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user},
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
    data["provider"] = "openai"
    data["model"] = model
    return data


def extract_all_routes_from_image(
    image_bytes: bytes,
    content_type: str,
    grid_cols: int,
    grid_rows: int,
    *,
    wall_name: str | None = None,
    wall_id: str | None = None,
    min_holds: int = 5,
) -> dict[str, Any]:
    """Detect every colored route on the wall → routes list + scene XML."""
    from app.services.route_xml import build_wall_xml, hold_shape

    try:
        img = _decode_image(image_bytes)
    except ValueError:
        single = extract_route_from_image(
            image_bytes, content_type, grid_cols, grid_rows, wall_name=wall_name
        )
        routes = [single]
        xml = build_wall_xml(wall_name=wall_name or "Wall", wall_id=wall_id, routes=routes)
        return {"routes": routes, "xml": xml, "provider": "fallback"}

    # Skip magenta duplicate of pink
    color_keys = ("pink", "blue", "green", "yellow", "orange", "red", "purple", "teal")
    routes: list[dict[str, Any]] = []
    for key in color_keys:
        holds = _detect_holds_cv(img, key)
        if len(holds) < min_holds:
            continue
        # Attach cartoon shape
        for h in holds:
            h["shape"] = hold_shape(h.get("hold_type"))
        holds = _legacy_grid_from_spatial(holds, grid_cols, grid_rows)
        label = key.title()
        routes.append(
            {
                "temp_id": f"route-{key}",
                "name": f"{label} Route",
                "color_identifier": label,
                "display_color": DISPLAY_HEX.get(key, "#888888"),
                "assigned_grade": "V?",
                "styles": ["technical"],
                "holds": holds,
                "notes": f"Auto-detected {label} ({len(holds)} holds)",
                "provider": "opencv",
            }
        )

    # Sort left→right by mean hold x
    routes.sort(
        key=lambda r: sum(h["x"] for h in r["holds"]) / max(len(r["holds"]), 1),
    )

    if not routes:
        single = extract_route_from_image(
            image_bytes, content_type, grid_cols, grid_rows, wall_name=wall_name
        )
        for h in single.get("holds") or []:
            h["shape"] = hold_shape(h.get("hold_type"))
        routes = [single]

    xml = build_wall_xml(wall_name=wall_name or "Wall", wall_id=wall_id, routes=routes)
    return {
        "routes": routes,
        "xml": xml,
        "provider": routes[0].get("provider", "opencv") if routes else "opencv",
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
    color_key = _normalize_color_key(color_hint) or "blue"
    holds: list[dict[str, Any]] = []
    provider = "opencv"

    try:
        img = _decode_image(image_bytes)
        color_key = _normalize_color_key(color_hint) or _guess_dominant_route_color(img)
        holds = _detect_holds_cv(img, color_key)
    except ValueError:
        holds = []
        provider = "fallback"

    # If CV under-detects, try OpenAI spatial (when keyed)
    if len(holds) < 3:
        ai = _openai_spatial_extract(image_bytes, content_type, color_hint or color_key, wall_name)
        if ai and isinstance(ai.get("holds"), list) and len(ai["holds"]) >= 3:
            provider = "openai"
            holds = []
            for i, h in enumerate(ai["holds"]):
                holds.append(
                    {
                        "sequence_index": int(h.get("sequence_index", i)),
                        "x": float(np.clip(float(h.get("x", 0.5)), 0, 1)),
                        "y": float(np.clip(float(h.get("y", 0.5)), 0, 1)),
                        "size": float(np.clip(float(h.get("size", 0.05)), 0.015, 0.35)),
                        "hold_type": h.get("hold_type") or "other",
                        "notes": h.get("notes"),
                    }
                )
            color_key = _normalize_color_key(ai.get("color_identifier")) or color_key
            holds = _legacy_grid_from_spatial(holds, grid_cols, grid_rows)
            return {
                "name": ai.get("name") or f"{color_key.title()} Route",
                "color_identifier": ai.get("color_identifier") or color_key.title(),
                "display_color": ai.get("display_color") or DISPLAY_HEX.get(color_key, "#888888"),
                "assigned_grade": ai.get("assigned_grade") or "V?",
                "styles": ai.get("styles") if isinstance(ai.get("styles"), list) else ["technical"],
                "holds": holds,
                "notes": ai.get("notes"),
                "provider": provider,
                "model": ai.get("model"),
            }

    if not holds:
        # Last-resort diagonal so upload never hard-fails
        holds = []
        for i in range(8):
            holds.append(
                {
                    "sequence_index": i,
                    "x": round(0.15 + i * 0.04, 4),
                    "y": round(0.9 - i * 0.1, 4),
                    "size": 0.05,
                    "hold_type": "crimp",
                    "notes": "start" if i == 0 else ("finish" if i == 7 else None),
                }
            )
        provider = "fallback"

    holds = _legacy_grid_from_spatial(holds, grid_cols, grid_rows)
    label = (color_hint or color_key).title()
    return {
        "name": f"{label} Route",
        "color_identifier": label,
        "display_color": DISPLAY_HEX.get(color_key, "#888888"),
        "assigned_grade": "V?",
        "styles": ["technical"],
        "holds": holds,
        "notes": f"Detected via {provider} ({len(holds)} holds, color={color_key})",
        "provider": provider,
    }
