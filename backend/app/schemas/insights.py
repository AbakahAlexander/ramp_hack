from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class InsightRouteIn(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(description="Frontend route id, e.g. r-102")
    name: str | None = None
    grade: str | None = None
    wall: str | None = None
    zone: str | None = None
    style: str | None = None
    colorName: str | None = None
    identifier: str | None = None
    age: str | None = None
    status: str | None = None
    setter: str | None = None


class AnalyzeInsightsRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "feedback_text": (
                        "Yellow V3 on the slab felt super reachy and sandbagged — "
                        "taller climbers only. Red cave route has a sharp finishing hold. "
                        "Orange V2 is a blast, please keep it. Purple board climb is tired."
                    ),
                    "routes": [
                        {
                            "id": "r-102",
                            "name": "Reach Check",
                            "grade": "V3",
                            "wall": "Slab Wall",
                            "colorName": "Yellow",
                            "style": "Technical",
                            "status": "Review",
                        }
                    ],
                }
            ]
        }
    )

    feedback_text: str = Field(
        description="Raw pasted climber feedback (comments, survey dump, notes)",
        min_length=10,
    )
    routes: list[InsightRouteIn] = Field(
        description="Static dashboard route catalog from the frontend",
        min_length=1,
    )


class RouteInsightOut(BaseModel):
    route_id: str
    recommendation: Literal["keep", "monitor", "change_out"] = Field(
        description="keep = leave up; monitor = watch/tweak; change_out = strip/replace"
    )
    confidence: Literal["low", "medium", "high"]
    headline: str = Field(description="Short decision title shown in the route panel")
    insights: list[str] = Field(description="Bullets explaining the decision")
    suggested_change: str | None = Field(
        default=None,
        description="What to change the route to / how to rework it",
    )
    themes: list[str] = Field(default_factory=list, description="Feedback themes tied to this route")


class AnalyzeInsightsResponse(BaseModel):
    gym_summary: str = Field(description="Overall setting priorities from the feedback")
    routes: list[RouteInsightOut]
    provider: str = Field(description="openai or fallback")
    model: str | None = None


class InsightsStoreOut(BaseModel):
    gym_summary: str | None = None
    routes: dict[str, RouteInsightOut] = Field(default_factory=dict)
    provider: str | None = None
    feedback_preview: str | None = None
