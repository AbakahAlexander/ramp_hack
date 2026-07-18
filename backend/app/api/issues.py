from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_demo_gym
from app.models.feedback import IssueReport
from app.models.gym import Gym
from app.models.route import Route
from app.schemas import IssueCreate, IssueOut, IssueUpdate

router = APIRouter(prefix="/issues", tags=["Issues"])


def _issue_for_gym(db: Session, issue_id: str, gym_id: str) -> IssueReport:
    issue = (
        db.query(IssueReport)
        .options(joinedload(IssueReport.route).joinedload(Route.wall))
        .filter(IssueReport.id == issue_id)
        .first()
    )
    if not issue or not issue.route or not issue.route.wall or issue.route.wall.gym_id != gym_id:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.get("", response_model=list[IssueOut], summary="List issue reports")
def list_issues(
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
    status: str | None = None,
    route_id: str | None = None,
):
    issues = (
        db.query(IssueReport)
        .options(joinedload(IssueReport.route).joinedload(Route.wall))
        .all()
    )
    filtered = [
        i for i in issues if i.route and i.route.wall and i.route.wall.gym_id == gym.id
    ]
    if status:
        filtered = [i for i in filtered if i.status == status]
    if route_id:
        filtered = [i for i in filtered if i.route_id == route_id]
    filtered.sort(key=lambda i: i.created_at, reverse=True)
    return filtered


@router.post("/routes/{route_id}", response_model=IssueOut, status_code=201)
def create_issue(
    route_id: str,
    payload: IssueCreate,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    route = (
        db.query(Route)
        .options(joinedload(Route.wall))
        .filter(Route.id == route_id)
        .first()
    )
    if not route or not route.wall or route.wall.gym_id != gym.id:
        raise HTTPException(status_code=404, detail="Route not found")
    issue = IssueReport(
        route_id=route_id,
        issue_type=payload.issue_type,
        note=payload.note,
        status="open",
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.patch("/{issue_id}", response_model=IssueOut)
def update_issue(
    issue_id: str,
    payload: IssueUpdate,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    issue = _issue_for_gym(db, issue_id, gym.id)
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(issue, k, v)
    issue.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(issue)
    return issue
