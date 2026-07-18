from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ----- Auth -----


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class StaffUserOut(ORMModel):
    id: str
    gym_id: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    is_setter: bool


# ----- Gym / Wall -----


class GymOut(ORMModel):
    id: str
    name: str
    locations: list[str]
    grade_system: str
    tag_vocabulary: list[str]


class WallCreate(BaseModel):
    name: str
    zone: str = ""
    angle_type: str = "vertical"
    is_active: bool = True


class WallOut(ORMModel):
    id: str
    gym_id: str
    name: str
    zone: str
    angle_type: str
    is_active: bool


# ----- Routes -----


class RouteCreate(BaseModel):
    wall_id: str
    color_identifier: str
    assigned_grade: str
    grade_system: str = "V-scale"
    styles: list[str] = Field(default_factory=list)
    set_date: date
    reset_date: date | None = None
    photo_url: str | None = None
    setter_ids: list[str] = Field(default_factory=list)
    notes: str | None = None
    status: Literal["active", "needs_review", "scheduled_for_strip", "archived"] = "active"


class RouteUpdate(BaseModel):
    wall_id: str | None = None
    color_identifier: str | None = None
    assigned_grade: str | None = None
    grade_system: str | None = None
    styles: list[str] | None = None
    set_date: date | None = None
    reset_date: date | None = None
    photo_url: str | None = None
    setter_ids: list[str] | None = None
    notes: str | None = None
    status: Literal["active", "needs_review", "scheduled_for_strip", "archived"] | None = None


class RouteStatusUpdate(BaseModel):
    status: Literal["active", "needs_review", "scheduled_for_strip", "archived"]


class SetterBrief(ORMModel):
    id: str
    full_name: str


class RouteHealth(BaseModel):
    sends: int = 0
    attempts: int = 0
    projects: int = 0
    unique_contributors: int = 0
    perceived_grades: dict[str, int] = Field(default_factory=dict)
    median_perceived_grade: str | None = None
    enjoyment_avg: float | None = None
    enjoyment_count: int = 0
    tag_counts: dict[str, int] = Field(default_factory=dict)
    open_issues: int = 0
    age_days: int = 0
    engagement_trend: Literal["rising", "steady", "declining", "unknown"] = "unknown"
    insight_quality: Literal["low", "medium", "high"] = "low"
    review_score: float = 0.0


class RouteOut(ORMModel):
    id: str
    wall_id: str
    photo_url: str | None
    color_identifier: str
    assigned_grade: str
    grade_system: str
    styles: list[str]
    status: str
    set_date: date
    reset_date: date | None
    notes: str | None
    setters: list[SetterBrief]
    created_at: datetime
    updated_at: datetime


class RouteDetailOut(RouteOut):
    health: RouteHealth
    wall_name: str | None = None
    zone: str | None = None


class RouteListOut(BaseModel):
    items: list[RouteDetailOut]
    total: int


# ----- Feedback -----


class FeedbackCreate(BaseModel):
    outcome: Literal["sent", "tried", "projecting"]
    perceived_grade: str | None = None
    enjoyment: int | None = Field(default=None, ge=1, le=5)
    tags: list[str] = Field(default_factory=list)
    comment: str | None = None
    contributor_id: str | None = None  # optional; server generates anonymous if omitted


class FeedbackOut(ORMModel):
    id: str
    route_id: str
    outcome: str
    perceived_grade: str | None
    enjoyment: int | None
    tags: list[str]
    comment: str | None
    created_at: datetime
    # contributor_id intentionally omitted from staff-facing aggregates elsewhere;
    # included only for write confirmation without exposing in setter analytics.


class FeedbackPublicOut(BaseModel):
    id: str
    route_id: str
    outcome: str
    created_at: datetime
    message: str = "Thanks for the feedback!"


# ----- Issues -----


class IssueCreate(BaseModel):
    issue_type: Literal["sharp", "broken_hold", "spinner", "unsafe", "other"]
    note: str | None = None


class IssueUpdate(BaseModel):
    status: Literal["open", "acknowledged", "resolved"] | None = None
    owner_id: str | None = None
    note: str | None = None


class IssueOut(ORMModel):
    id: str
    route_id: str
    issue_type: str
    note: str | None
    status: str
    owner_id: str | None
    created_at: datetime
    updated_at: datetime


# ----- Dashboard / Insights -----


class WallHealthBucket(BaseModel):
    wall_id: str
    wall_name: str
    zone: str
    angle_type: str
    grade_counts: dict[str, int]
    style_counts: dict[str, int]
    total_active: int
    gaps: list[str]


class OverviewOut(BaseModel):
    wall_health: list[WallHealthBucket]
    routes_needing_review: list[RouteDetailOut]
    recent_feedback: list[FeedbackOut]
    upcoming_strips: list[RouteDetailOut]
    open_issue_count: int


class ResetQueueItem(BaseModel):
    route: RouteDetailOut
    review_score: float
    reasons: list[str]


class CoverageCell(BaseModel):
    wall_id: str
    wall_name: str
    grade: str
    style: str
    count: int


class CoverageMatrixOut(BaseModel):
    cells: list[CoverageCell]
    gaps: list[str]


class SetterInsightOut(BaseModel):
    setter_id: str
    setter_name: str
    route_count: int
    grade_calibration_notes: list[str]
    avg_enjoyment: float | None
    style_mix: dict[str, int]
    wall_mix: dict[str, int]
    sample_size: int
    insight_quality: Literal["low", "medium", "high"]


# ----- Public climber route card -----


class PublicRouteCard(BaseModel):
    id: str
    color_identifier: str
    assigned_grade: str
    grade_system: str
    styles: list[str]
    wall_name: str
    zone: str
    photo_url: str | None
    tag_vocabulary: list[str]
    gym_name: str
