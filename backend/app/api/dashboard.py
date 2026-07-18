from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_demo_gym
from app.models.feedback import Feedback, IssueReport, IssueStatus
from app.models.gym import Gym, Wall
from app.models.route import Route, RouteStatus
from app.schemas import (
    CoverageMatrixOut,
    OverviewOut,
    ResetQueueItem,
    SetterInsightOut,
)
from app.services.metrics import (
    build_coverage_matrix,
    build_reset_reasons,
    build_setter_insights,
    build_wall_health,
    compute_route_health,
    feedback_to_out,
    route_to_detail,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/overview",
    response_model=OverviewOut,
    summary="Staff home — what needs attention?",
    response_description="Wall health, review queue, recent feedback, upcoming strips",
    description=(
        "Main dashboard payload for the staff UI.\n\n"
        "- `wall_health` — grade/style balance + gap messages\n"
        "- `routes_needing_review` — high review_score or needs_review status\n"
        "- `recent_feedback` — latest climber comments/tags\n"
        "- `upcoming_strips` — scheduled_for_strip or reset_date set\n"
        "- `open_issue_count` — unresolved safety issues"
    ),
)
def overview(
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    wall_ids = [w.id for w in db.query(Wall).filter(Wall.gym_id == gym.id).all()]
    routes = (
        db.query(Route)
        .options(joinedload(Route.wall), joinedload(Route.setters))
        .filter(Route.wall_id.in_(wall_ids), Route.status != RouteStatus.ARCHIVED.value)
        .all()
    )

    details = [route_to_detail(r, db) for r in routes]
    needing_review = sorted(
        [d for d in details if d.status == RouteStatus.NEEDS_REVIEW.value or d.health.review_score >= 50],
        key=lambda d: d.health.review_score,
        reverse=True,
    )[:10]

    upcoming = sorted(
        [d for d in details if d.status == RouteStatus.SCHEDULED_FOR_STRIP.value or d.reset_date],
        key=lambda d: (d.reset_date is None, d.reset_date),
    )[:10]

    feedback_rows = (
        db.query(Feedback)
        .join(Route)
        .filter(Route.wall_id.in_(wall_ids))
        .order_by(Feedback.created_at.desc())
        .limit(15)
        .all()
    )

    open_issues = 0
    for r in routes:
        open_issues += (
            db.query(IssueReport)
            .filter(IssueReport.route_id == r.id, IssueReport.status != IssueStatus.RESOLVED.value)
            .count()
        )

    return OverviewOut(
        wall_health=build_wall_health(db, gym.id),
        routes_needing_review=needing_review,
        recent_feedback=[feedback_to_out(f) for f in feedback_rows],
        upcoming_strips=upcoming,
        open_issue_count=open_issues,
    )


@router.get(
    "/reset-queue",
    response_model=list[ResetQueueItem],
    summary="Reset planner queue",
    response_description="Routes ranked by review_score with human-readable reasons",
    description=(
        "Ranks active routes for the next setting cycle. "
        "This is a **prompt for staff judgment**, not an automatic strip decision."
    ),
)
def reset_queue(
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=20, le=100, description="Max items to return"),
):
    wall_ids = [w.id for w in db.query(Wall).filter(Wall.gym_id == gym.id).all()]
    routes = (
        db.query(Route)
        .options(joinedload(Route.wall), joinedload(Route.setters))
        .filter(Route.wall_id.in_(wall_ids), Route.status != RouteStatus.ARCHIVED.value)
        .all()
    )
    items: list[ResetQueueItem] = []
    for route in routes:
        health = compute_route_health(route, db)
        detail = route_to_detail(route, db)
        items.append(
            ResetQueueItem(
                route=detail,
                review_score=health.review_score,
                reasons=build_reset_reasons(route, health),
            )
        )
    items.sort(key=lambda i: i.review_score, reverse=True)
    return items[:limit]


@router.get(
    "/coverage",
    response_model=CoverageMatrixOut,
    summary="Wall × grade × style coverage",
    response_description="Sparse coverage cells plus gap messages",
    description="Helps plan an inclusive setting day by showing where grades/styles are missing.",
)
def coverage(
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    return build_coverage_matrix(db, gym.id)


@router.get(
    "/setter-insights",
    response_model=list[SetterInsightOut],
    summary="Setter coaching insights",
    response_description="Per-setter contextual metrics (not a public ranking)",
    description=(
        "Internal coaching view. Compares grade feel and mix in context. "
        "There is **no single best-setter score**."
    ),
)
def setter_insights(
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    return build_setter_insights(db, gym.id)
