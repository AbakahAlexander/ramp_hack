"""Generate keep / change-out insights from pasted climber feedback via OpenAI."""

from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from app.config import get_settings

SYSTEM_PROMPT = """You are Crux, an assistant for indoor climbing gym routesetters.
Given the gym's active routes and raw climber feedback (comments, notes, surveys),
produce actionable setting decisions.

For EACH route in the catalog, decide:
- keep: feedback is positive / healthy — leave it up
- monitor: mixed or thin signal — watch, maybe tweak
- change_out: stale, disliked, unsafe, misgraded, or blocking coverage — strip/replace

Also say WHAT to change it to when recommendation is change_out or monitor with a clear fix
(e.g. "Replace with a V2 slab that avoids long reaches" or "Regrade to V4 and soften the crux hold").

Be specific to the feedback. Do not invent routes that are not in the catalog.
Map feedback to routes using color, grade, name, wall, or style mentions.
If a route is not mentioned, infer lightly from overall wall balance or mark monitor with low confidence.

Return ONLY valid JSON matching this schema:
{
  "gym_summary": "1-3 sentences on overall wall priorities",
  "routes": [
    {
      "route_id": "exact id from catalog",
      "recommendation": "keep" | "monitor" | "change_out",
      "confidence": "low" | "medium" | "high",
      "headline": "short decision title",
      "insights": ["bullet", "bullet"],
      "suggested_change": "string or null",
      "themes": ["tag", "tag"]
    }
  ]
}
Include every route_id from the catalog exactly once.
"""


def _client() -> OpenAI | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    return OpenAI(api_key=settings.openai_api_key)


def _fallback_insights(routes: list[dict[str, Any]], feedback_text: str) -> dict[str, Any]:
    """Deterministic insights when OPENAI_API_KEY is missing (local/tests)."""
    text = feedback_text.lower()
    sentences = [s.strip() for s in re.split(r"[.\n]+", text) if s.strip()]
    neg_words = ("sharp", "sandbag", "reachy", "morpho", "confusing", "hate", "scary", "broken", "spinner", "tired", "boring")
    pos_words = ("fun", "love", "great", "awesome", "classic", "keep", "blast", "perfect")

    results = []
    for route in routes:
        rid = route["id"]
        name = str(route.get("name", "")).lower()
        color = str(route.get("colorName") or route.get("color_identifier") or "").lower()
        grade = str(route.get("grade") or route.get("assigned_grade") or "").lower()
        tokens = [t for t in [name, color, grade, name.split()[0] if name else ""] if t and len(t) > 2]

        related = [s for s in sentences if any(tok in s for tok in tokens)]
        scope = " ".join(related) if related else ""

        mentioned = bool(related)
        negative = any(w in scope for w in neg_words)
        positive = any(w in scope for w in pos_words)

        if mentioned and negative and not positive:
            rec = "change_out"
            headline = f"Change out {route.get('name')}"
            suggested = (
                f"Replace {route.get('grade')} {route.get('style', 'route')} with a fairer "
                f"movement-focused climb at a similar or easier grade on {route.get('wall')}."
            )
            insights = [
                "Feedback near this route's name/color/grade is negative.",
                "Prioritize strip or rework before the next setting cycle.",
            ]
            themes = [t for t in neg_words if t in scope]
        elif mentioned and positive:
            rec = "keep"
            headline = f"Keep {route.get('name')}"
            suggested = None
            insights = ["Climbers mention this route positively.", "Sustained enjoyment — leave it up."]
            themes = [t for t in pos_words if t in scope] or ["positive"]
        elif str(route.get("status", "")).lower() in ("strip soon", "scheduled_for_strip"):
            rec = "change_out"
            headline = f"Scheduled strip: {route.get('name')}"
            suggested = f"Refresh {route.get('wall')} with a new {route.get('grade')} in a complementary style."
            insights = ["Already flagged for strip in inventory.", "Use feedback to choose the replacement style."]
            themes = ["aging"]
        elif mentioned and negative and positive:
            rec = "monitor"
            headline = f"Watch {route.get('name')}"
            suggested = "Mixed signal — consider a small tweak rather than a full strip."
            insights = ["Feedback is mixed for this route.", "Gather a bit more signal before stripping."]
            themes = ["mixed"]
        else:
            rec = "keep" if not mentioned else "monitor"
            headline = f"{'Keep' if rec == 'keep' else 'Monitor'} {route.get('name')}"
            suggested = None
            insights = [
                "No strong route-specific complaint in the pasted feedback."
                if rec == "keep"
                else "Limited direct mentions — keep an eye on engagement."
            ]
            themes = []

        conf = "high" if mentioned and (negative or positive) else ("medium" if mentioned else "low")

        results.append(
            {
                "route_id": rid,
                "recommendation": rec,
                "confidence": conf,
                "headline": headline,
                "insights": insights,
                "suggested_change": suggested,
                "themes": themes,
            }
        )

    keep_n = sum(1 for r in results if r["recommendation"] == "keep")
    out_n = sum(1 for r in results if r["recommendation"] == "change_out")
    return {
        "gym_summary": (
            f"From the pasted feedback, prioritize {out_n} change-out(s) and protect {keep_n} keepers. "
            "Use route detail panels for per-route AI guidance."
        ),
        "routes": results,
        "provider": "fallback",
    }


def generate_insights(routes: list[dict[str, Any]], feedback_text: str) -> dict[str, Any]:
    feedback_text = (feedback_text or "").strip()
    if not feedback_text:
        raise ValueError("feedback_text is required")
    if not routes:
        raise ValueError("routes catalog is required")

    client = _client()
    if client is None:
        return _fallback_insights(routes, feedback_text)

    settings = get_settings()
    catalog = []
    for r in routes:
        styles = r.get("styles")
        style = r.get("style")
        if not style and isinstance(styles, list) and styles:
            style = styles[0]
        catalog.append(
            {
                "id": r.get("id"),
                "name": r.get("name"),
                "grade": r.get("grade") or r.get("assigned_grade"),
                "wall": r.get("wall") or r.get("wall_name"),
                "zone": r.get("zone"),
                "style": style,
                "color": r.get("colorName") or r.get("color_identifier") or r.get("identifier"),
                "age": r.get("age"),
                "status": r.get("status"),
                "setter": r.get("setter"),
            }
        )

    user_payload = {
        "routes": catalog,
        "climber_feedback": feedback_text,
    }

    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Analyze this feedback against the route catalog and return JSON.\n\n"
                    + json.dumps(user_payload, indent=2)
                ),
            },
        ],
    )

    raw = response.choices[0].message.content or "{}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # try extract JSON object
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group(0)) if match else {"gym_summary": raw, "routes": []}

    # Ensure every route is present
    by_id = {item.get("route_id"): item for item in data.get("routes") or [] if item.get("route_id")}
    normalized = []
    for route in routes:
        rid = route["id"]
        item = by_id.get(rid) or {
            "route_id": rid,
            "recommendation": "monitor",
            "confidence": "low",
            "headline": f"Limited signal for {route.get('name', rid)}",
            "insights": ["Model did not return a decision for this route."],
            "suggested_change": None,
            "themes": [],
        }
        rec = item.get("recommendation", "monitor")
        if rec not in ("keep", "monitor", "change_out"):
            rec = "monitor"
        item["recommendation"] = rec
        item["route_id"] = rid
        item.setdefault("insights", [])
        item.setdefault("themes", [])
        item.setdefault("suggested_change", None)
        item.setdefault("confidence", "medium")
        item.setdefault("headline", "")
        normalized.append(item)

    return {
        "gym_summary": data.get("gym_summary") or "AI reviewed climber feedback against active routes.",
        "routes": normalized,
        "provider": "openai",
        "model": settings.openai_model,
    }
