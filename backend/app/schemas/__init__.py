"""Pydantic schemas with OpenAPI descriptions and examples for Swagger."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Always 'bearer'")


class LoginRequest(BaseModel):
    email: EmailStr = Field(description="Staff email", examples=["manager@summitlab.demo"])
    password: str = Field(description="Staff password", examples=["cruxdemo123"])


class StaffUserOut(ORMModel):
    id: str = Field(description="Staff user UUID")
    gym_id: str = Field(description="Gym this staff member belongs to")
    email: EmailStr = Field(description="Login email")
    full_name: str = Field(description="Display name", examples=["Jordan Setter"])
    role: str = Field(description="Role: manager | setter | floor", examples=["setter"])
    is_active: bool = Field(description="Whether the account can be used")
    is_setter: bool = Field(description="True if this person sets routes (appears in setter insights)")


class GymOut(ORMModel):
    id: str = Field(description="Gym UUID")
    name: str = Field(description="Gym display name", examples=["Summit Lab Climbing"])
    locations: list[str] = Field(description="Location labels", examples=[["Main Street"]])
    grade_system: str = Field(description="Default grade system", examples=["V-scale"])
    tag_vocabulary: list[str] = Field(
        description="Allowed feedback tags for climbers",
        examples=[["fun", "technical", "reachy", "sharp"]],
    )


class WallCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Cave Overhang",
                    "zone": "Back",
                    "angle_type": "overhang",
                    "is_active": True,
                }
            ]
        }
    )

    name: str = Field(description="Wall name", examples=["Slab Wall"])
    zone: str = Field(default="", description="Area of the gym", examples=["Front"])
    angle_type: str = Field(
        default="vertical",
        description="Wall angle/type: slab | vertical | overhang | cave",
        examples=["slab"],
    )
    is_active: bool = Field(default=True, description="Inactive walls are hidden from default lists")


class WallOut(ORMModel):
    id: str = Field(description="Wall UUID")
    gym_id: str = Field(description="Parent gym UUID")
    name: str = Field(description="Wall name")
    zone: str = Field(description="Gym zone / section")
    angle_type: str = Field(description="slab | vertical | overhang | cave")
    is_active: bool = Field(description="Whether the wall is in use")


class RouteCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "wall_id": "paste-a-wall-id-from-GET-/walls",
                    "color_identifier": "Teal",
                    "assigned_grade": "V2",
                    "grade_system": "V-scale",
                    "styles": ["slab", "technical"],
                    "set_date": "2026-07-18",
                    "reset_date": None,
                    "photo_url": "https://placehold.co/400x600/png?text=Teal+V2",
                    "setter_ids": ["paste-a-staff-id-from-GET-/staff"],
                    "notes": "Crux on the second hold",
                    "status": "active",
                }
            ]
        }
    )

    wall_id: str = Field(description="Wall UUID from GET /api/v1/walls")
    color_identifier: str = Field(
        description="Hold color or tape identifier on the placard",
        examples=["Yellow"],
    )
    assigned_grade: str = Field(description="Setter-assigned grade", examples=["V3"])
    grade_system: str = Field(default="V-scale", description="Grade system label", examples=["V-scale"])
    styles: list[str] = Field(
        default_factory=list,
        description="Movement/style tags",
        examples=[["slab", "technical"]],
    )
    set_date: date = Field(description="Date the route was set (YYYY-MM-DD)", examples=["2026-07-18"])
    reset_date: date | None = Field(
        default=None,
        description="Optional planned strip/reset date",
        examples=["2026-08-01"],
    )
    photo_url: str | None = Field(
        default=None,
        description="Optional image URL (no file upload in MVP)",
        examples=["https://placehold.co/400x600/png?text=Yellow+V3"],
    )
    setter_ids: list[str] = Field(
        default_factory=list,
        description="Staff UUIDs of setters (from GET /api/v1/staff?setters_only=true)",
    )
    notes: str | None = Field(default=None, description="Internal setter notes")
    status: Literal["active", "needs_review", "scheduled_for_strip", "archived"] = Field(
        default="active",
        description="Lifecycle status",
    )


class RouteUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "assigned_grade": "V4",
                    "styles": ["slab", "reachy"],
                    "status": "needs_review",
                    "notes": "Grade feel mismatch — review next cycle",
                }
            ]
        }
    )

    wall_id: str | None = Field(default=None, description="Move route to another wall")
    color_identifier: str | None = None
    assigned_grade: str | None = None
    grade_system: str | None = None
    styles: list[str] | None = Field(default=None, description="Replaces the full style list")
    set_date: date | None = None
    reset_date: date | None = None
    photo_url: str | None = None
    setter_ids: list[str] | None = Field(default=None, description="Replaces setter list")
    notes: str | None = None
    status: Literal["active", "needs_review", "scheduled_for_strip", "archived"] | None = None


class RouteStatusUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"status": "scheduled_for_strip"}]}
    )

    status: Literal["active", "needs_review", "scheduled_for_strip", "archived"] = Field(
        description="New lifecycle status"
    )


class SetterBrief(ORMModel):
    id: str = Field(description="Staff UUID")
    full_name: str = Field(description="Setter display name")


class RouteHealth(BaseModel):
    sends: int = Field(default=0, description="Count of 'sent' feedback")
    attempts: int = Field(default=0, description="Count of 'tried' feedback")
    projects: int = Field(default=0, description="Count of 'projecting' feedback")
    unique_contributors: int = Field(default=0, description="Distinct anonymized climbers")
    perceived_grades: dict[str, int] = Field(
        default_factory=dict,
        description="Histogram of climber-perceived grades",
        examples=[{"V3": 2, "V4": 4}],
    )
    median_perceived_grade: str | None = Field(
        default=None,
        description="Median perceived grade (V-scale), or null if insufficient data",
        examples=["V4"],
    )
    enjoyment_avg: float | None = Field(
        default=None,
        description="Average enjoyment 1–5, or null if none",
        examples=[3.75],
    )
    enjoyment_count: int = Field(default=0, description="Number of enjoyment ratings")
    tag_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Frequency of feedback tags",
        examples=[{"reachy": 4, "technical": 3}],
    )
    open_issues: int = Field(default=0, description="Unresolved issue reports")
    age_days: int = Field(default=0, description="Days since set_date")
    engagement_trend: Literal["rising", "steady", "declining", "unknown"] = Field(
        default="unknown",
        description="Recent vs prior week activity",
    )
    insight_quality: Literal["low", "medium", "high"] = Field(
        default="low",
        description="Confidence based on sample size and recency — do not over-read 'low'",
    )
    review_score: float = Field(
        default=0.0,
        description="0–100 prompt score for reset planner (higher = needs attention sooner)",
        examples=[62.5],
    )


class RouteOut(ORMModel):
    id: str = Field(description="Route UUID — use this in QR URLs")
    wall_id: str
    photo_url: str | None = Field(description="Optional photo link")
    color_identifier: str
    assigned_grade: str
    grade_system: str
    styles: list[str]
    status: str = Field(description="active | needs_review | scheduled_for_strip | archived")
    set_date: date
    reset_date: date | None
    notes: str | None
    setters: list[SetterBrief]
    created_at: datetime
    updated_at: datetime


class RouteDetailOut(RouteOut):
    health: RouteHealth = Field(description="Computed engagement / grade / issue signals")
    wall_name: str | None = Field(default=None, description="Denormalized wall name")
    zone: str | None = Field(default=None, description="Denormalized wall zone")


class RouteListOut(BaseModel):
    items: list[RouteDetailOut] = Field(description="Filtered route list with health")
    total: int = Field(description="Number of items returned")


class FeedbackCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "outcome": "sent",
                    "perceived_grade": "V4",
                    "enjoyment": 4,
                    "tags": ["technical", "reachy"],
                    "comment": "Long moves on the crux",
                }
            ]
        }
    )

    outcome: Literal["sent", "tried", "projecting"] = Field(
        description="Climber result: sent (completed), tried (attempted), projecting (working it)"
    )
    perceived_grade: str | None = Field(
        default=None,
        description="How hard it felt vs the placard",
        examples=["V4"],
    )
    enjoyment: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="Optional quality/enjoyment rating from 1 (poor) to 5 (great)",
        examples=[4],
    )
    tags: list[str] = Field(
        default_factory=list,
        description="From gym tag_vocabulary. Safety tags like 'sharp' auto-create an issue.",
        examples=[["technical", "reachy"]],
    )
    comment: str | None = Field(default=None, description="Optional short free-text note")
    contributor_id: str | None = Field(
        default=None,
        description="Optional anonymized id; server generates one if omitted",
    )


class FeedbackOut(ORMModel):
    id: str
    route_id: str
    outcome: str = Field(description="sent | tried | projecting")
    perceived_grade: str | None
    enjoyment: int | None = Field(description="1–5 or null")
    tags: list[str]
    comment: str | None
    created_at: datetime


class FeedbackPublicOut(BaseModel):
    id: str = Field(description="Created feedback UUID")
    route_id: str
    outcome: str
    created_at: datetime
    message: str = Field(default="Thanks for the feedback!", description="Confirmation for the climber UI")


class IssueCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"issue_type": "sharp", "note": "Finishing hold feels razor sharp"}]
        }
    )

    issue_type: Literal["sharp", "broken_hold", "spinner", "unsafe", "other"] = Field(
        description="Issue category for the staff queue"
    )
    note: str | None = Field(default=None, description="What floor staff / climber reported")


class IssueUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"status": "acknowledged"}]}
    )

    status: Literal["open", "acknowledged", "resolved"] | None = Field(
        default=None, description="Workflow status"
    )
    owner_id: str | None = Field(default=None, description="Staff UUID assigned to follow up")
    note: str | None = None


class IssueOut(ORMModel):
    id: str
    route_id: str
    issue_type: str
    note: str | None
    status: str = Field(description="open | acknowledged | resolved")
    owner_id: str | None
    created_at: datetime
    updated_at: datetime


class WallHealthBucket(BaseModel):
    wall_id: str
    wall_name: str
    zone: str
    angle_type: str
    grade_counts: dict[str, int] = Field(description="Active routes per assigned grade")
    style_counts: dict[str, int] = Field(description="Active routes per style tag")
    total_active: int
    gaps: list[str] = Field(
        description="Human-readable coverage gaps, e.g. 'No beginner routes on Slab Wall'"
    )


class OverviewOut(BaseModel):
    wall_health: list[WallHealthBucket] = Field(description="Per-wall grade/style balance + gaps")
    routes_needing_review: list[RouteDetailOut] = Field(
        description="Top routes flagged by status or high review_score"
    )
    recent_feedback: list[FeedbackOut] = Field(description="Latest climber feedback across the gym")
    upcoming_strips: list[RouteDetailOut] = Field(
        description="Routes scheduled for strip or with a reset_date"
    )
    open_issue_count: int = Field(description="Total unresolved safety/issue reports")


class ResetQueueItem(BaseModel):
    route: RouteDetailOut
    review_score: float = Field(description="Same 0–100 score as route.health.review_score")
    reasons: list[str] = Field(
        description="Why this route ranked high",
        examples=[["On wall 35 days", "Declining engagement", "1 open issue(s)"]],
    )


class CoverageCell(BaseModel):
    wall_id: str
    wall_name: str
    grade: str
    style: str
    count: int = Field(description="How many active routes match this wall×grade×style cell")


class CoverageMatrixOut(BaseModel):
    cells: list[CoverageCell] = Field(description="Sparse matrix of coverage counts")
    gaps: list[str] = Field(description="Heuristic gap messages for planning a set day")


class SetterInsightOut(BaseModel):
    setter_id: str
    setter_name: str
    route_count: int = Field(description="Routes attributed to this setter")
    grade_calibration_notes: list[str] = Field(
        description="Contextual notes where perceived grade differs from assigned (not a ranking)"
    )
    avg_enjoyment: float | None = Field(description="Average enjoyment across their routes")
    style_mix: dict[str, int] = Field(description="Styles this setter has contributed")
    wall_mix: dict[str, int] = Field(description="Walls this setter has contributed to")
    sample_size: int = Field(description="Total feedback events across their routes")
    insight_quality: Literal["low", "medium", "high"] = Field(
        description="Confidence — ignore calibration notes when low"
    )


class PublicRouteCard(BaseModel):
    id: str = Field(description="Route UUID")
    color_identifier: str
    assigned_grade: str
    grade_system: str
    styles: list[str]
    wall_name: str
    zone: str
    photo_url: str | None
    tag_vocabulary: list[str] = Field(description="Tags to show in the climber feedback UI")
    gym_name: str


class SeedStatusOut(BaseModel):
    gym_name: str | None = Field(description="Demo gym name if seeded")
    gyms: int
    walls: int
    routes: int
    staff: int
    feedback: int
    issues: int
    seeded: bool = Field(description="True when demo data is present")
    hint: str = Field(
        description="What to call next in Swagger",
        examples=["GET /api/v1/dashboard/overview"],
    )
