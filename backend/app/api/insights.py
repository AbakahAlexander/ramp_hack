"""AI insights from pasted climber feedback."""

from typing import Annotated

from fastapi import APIRouter, HTTPException

from app.schemas.insights import (
    AnalyzeInsightsRequest,
    AnalyzeInsightsResponse,
    InsightsStoreOut,
    RouteInsightOut,
)
from app.services.openai_insights import generate_insights

router = APIRouter(prefix="/insights", tags=["AI Insights"])

# Last analysis kept in memory for the demo (single gym)
_LAST: dict = {
    "gym_summary": None,
    "routes": {},
    "provider": None,
    "feedback_preview": None,
    "model": None,
}


@router.post(
    "/analyze",
    response_model=AnalyzeInsightsResponse,
    summary="Analyze pasted climber feedback with AI",
    response_description="Per-route keep / monitor / change_out decisions",
    description=(
        "Paste raw climber feedback and the static route catalog from the dashboard. "
        "Uses OpenAI when `OPENAI_API_KEY` is set; otherwise a deterministic fallback "
        "so local demos still work.\n\n"
        "Click a route in the UI to read its insight panel."
    ),
)
def analyze_feedback(payload: AnalyzeInsightsRequest):
    routes = [r.model_dump() for r in payload.routes]
    try:
        result = generate_insights(routes, payload.feedback_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Insight generation failed: {exc}") from exc

    route_models = [RouteInsightOut.model_validate(item) for item in result["routes"]]
    _LAST["gym_summary"] = result.get("gym_summary")
    _LAST["routes"] = {r.route_id: r for r in route_models}
    _LAST["provider"] = result.get("provider")
    _LAST["model"] = result.get("model")
    _LAST["feedback_preview"] = payload.feedback_text[:280]

    return AnalyzeInsightsResponse(
        gym_summary=result["gym_summary"],
        routes=route_models,
        provider=result.get("provider", "unknown"),
        model=result.get("model"),
    )


@router.get(
    "/latest",
    response_model=InsightsStoreOut,
    summary="Get the last AI analysis",
    description="Returns the most recent analyze result so the dashboard can show insights on route click.",
)
def latest_insights():
    return InsightsStoreOut(
        gym_summary=_LAST.get("gym_summary"),
        routes=_LAST.get("routes") or {},
        provider=_LAST.get("provider"),
        feedback_preview=_LAST.get("feedback_preview"),
    )


@router.get(
    "/routes/{route_id}",
    response_model=RouteInsightOut,
    summary="Get AI insight for one route",
    description="Insight for a single route from the last analysis. 404 if not analyzed yet.",
)
def route_insight(route_id: str):
    item = (_LAST.get("routes") or {}).get(route_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="No insight for this route yet. Paste feedback and run Analyze first.",
        )
    return item
