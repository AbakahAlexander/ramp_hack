"""Crux wall scene XML — editable representation of routes + holds.

Optimize a set later by rewriting this XML (positions, shapes, colors), then re-import.
Coordinates use a 0–100 viewBox (x left→right, y top→bottom).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any
from xml.dom import minidom

SHAPE_BY_TYPE = {
    "volume": "triangle",
    "jug": "rounded_rect",
    "pinch": "oval",
    "sloper": "oval",
    "crimp": "circle",
    "foothold": "circle",
    "pocket": "circle",
    "other": "polygon",
}


def hold_shape(hold_type: str | None) -> str:
    return SHAPE_BY_TYPE.get((hold_type or "other").lower(), "circle")


def build_wall_xml(
    *,
    wall_name: str,
    wall_id: str | None,
    routes: list[dict[str, Any]],
) -> str:
    """Build <wall> XML from extracted route dicts (holds with x,y,size,hold_type)."""
    root = ET.Element(
        "wall",
        {
            "name": wall_name or "Wall",
            "id": wall_id or "",
            "viewBox": "0 0 100 100",
        },
    )
    for route in routes:
        r_el = ET.SubElement(
            root,
            "route",
            {
                "id": str(route.get("temp_id") or route.get("id") or ""),
                "name": str(route.get("name") or route.get("color_identifier") or "Route"),
                "color": str(route.get("color_identifier") or "Mixed"),
                "hex": str(route.get("display_color") or "#888888"),
                "grade": str(route.get("assigned_grade") or "V?"),
            },
        )
        for h in route.get("holds") or []:
            size = float(h.get("size") or 0.05)
            # size is relative diameter 0–1 → width/height in viewBox units
            wh = max(1.5, min(18.0, size * 55.0))
            ht = h.get("hold_type") or "other"
            shape = h.get("shape") or hold_shape(ht)
            attrs = {
                "seq": str(int(h.get("sequence_index", 0))),
                "x": f"{float(h.get('x', 0.5)) * 100:.2f}",
                "y": f"{float(h.get('y', 0.5)) * 100:.2f}",
                "w": f"{wh:.2f}",
                "h": f"{wh:.2f}",
                "shape": shape,
                "type": ht,
            }
            if h.get("notes"):
                attrs["notes"] = str(h["notes"])
            ET.SubElement(r_el, "hold", attrs)

    rough = ET.tostring(root, encoding="unicode")
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ")


def parse_wall_xml(xml_text: str) -> dict[str, Any]:
    """Parse wall XML → { wall, routes: [{..., holds: [...]}] } with normalized 0–1 coords."""
    root = ET.fromstring(xml_text)
    if root.tag != "wall":
        raise ValueError("Root element must be <wall>")
    routes = []
    for r_el in root.findall("route"):
        holds = []
        for h_el in r_el.findall("hold"):
            w = float(h_el.get("w") or 5)
            h = float(h_el.get("h") or 5)
            size = max(w, h) / 55.0
            holds.append(
                {
                    "sequence_index": int(h_el.get("seq") or 0),
                    "x": float(h_el.get("x") or 50) / 100.0,
                    "y": float(h_el.get("y") or 50) / 100.0,
                    "size": size,
                    "hold_type": h_el.get("type") or "other",
                    "shape": h_el.get("shape") or hold_shape(h_el.get("type")),
                    "notes": h_el.get("notes"),
                }
            )
        holds.sort(key=lambda x: x["sequence_index"])
        routes.append(
            {
                "id": r_el.get("id") or None,
                "name": r_el.get("name") or "Route",
                "color_identifier": r_el.get("color") or "Mixed",
                "display_color": r_el.get("hex") or "#888888",
                "assigned_grade": r_el.get("grade") or "V?",
                "holds": holds,
            }
        )
    return {
        "wall_name": root.get("name") or "Wall",
        "wall_id": root.get("id") or None,
        "routes": routes,
        "xml": xml_text,
    }


def route_fragment_xml(route: dict[str, Any]) -> str:
    """Single <route> element as XML string."""
    wall_xml = build_wall_xml(wall_name="fragment", wall_id="", routes=[route])
    root = ET.fromstring(wall_xml)
    r_el = root.find("route")
    if r_el is None:
        return "<route/>"
    return ET.tostring(r_el, encoding="unicode")
