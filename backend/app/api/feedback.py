from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_demo_gym
from app.models.feedback import Feedback, IssueReport
from app.models.gym import Gym
from app.models.route import Route
from app.schemas import FeedbackCreate, FeedbackOut, FeedbackPublicOut
from app.services.metrics import feedback_to_out

router = APIRouter(tags=["Feedback"])

SAFETY_TAGS = {"sharp", "broken hold", "broken_hold", "unsafe", "spinner"}


def _route_in_gym(db: Session, route_id: str, gym_id: str | None = None) -> Route:
    route = (
        db.query(Route)
        .options(joinedload(Route.wall))
        .filter(Route.id == route_id)
        .first()
    )
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    if gym_id and route.wall.gym_id != gym_id:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.post(
    "/public/routes/{route_id}/feedback",
    response_model=FeedbackPublicOut,
    status_code=201,
    summary="Climber QR feedback (no auth)",
)
def submit_public_feedback(
    route_id: str,
    payload: FeedbackCreate,
    db: Annotated[Session, Depends(get_db)],
):
    route = _route_in_gym(db, route_id)
    if route.status == "archived":
        raise HTTPException(status_code=400, detail="Route is archived")

    contributor = payload.contributor_id or f"anon-{uuid4().hex[:12]}"
    tags = payload.tags or []
    fb = Feedback(
        route_id=route.id,
        outcome=payload.outcome,
        perceived_grade=payload.perceived_grade,
        enjoyment=payload.enjoyment,
        tags=",".join(tags),
        comment=payload.comment,
        contributor_id=contributor,
    )
    db.add(fb)

    for tag in tags:
        normalized = tag.strip().lower().replace(" ", "_")
        if normalized in SAFETY_TAGS or tag.strip().lower() in SAFETY_TAGS:
            issue_type = "sharp" if "sharp" in normalized else (
                "broken_hold" if "broken" in normalized else (
                    "spinner" if "spinner" in normalized else (
                        "unsafe" if "unsafe" in normalized else "other"
                    )
                )
            )
            db.add(
                IssueReport(
                    route_id=route.id,
                    issue_type=issue_type,
                    note=f"Auto-escalated from feedback tag: {tag}",
                    status="open",
                )
            )

    db.commit()
    db.refresh(fb)
    return FeedbackPublicOut(
        id=fb.id,
        route_id=fb.route_id,
        outcome=fb.outcome,
        created_at=fb.created_at,
    )


@router.get(
    "/routes/{route_id}/feedback",
    response_model=list[FeedbackOut],
    summary="List feedback for a route",
)
def list_route_feedback(
    route_id: str,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 50,
):
    _route_in_gym(db, route_id, gym.id)
    rows = (
        db.query(Feedback)
        .filter(Feedback.route_id == route_id)
        .order_by(Feedback.created_at.desc())
        .limit(limit)
        .all()
    )
    return [feedback_to_out(f) for f in rows]
