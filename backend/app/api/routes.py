from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_demo_gym
from app.models.gym import Gym, Wall
from app.models.route import Route
from app.models.user import StaffUser
from app.schemas import RouteCreate, RouteDetailOut, RouteListOut, RouteStatusUpdate, RouteUpdate
from app.services.metrics import route_to_detail

router = APIRouter(prefix="/routes", tags=["Routes"])


def _gym_walls(db: Session, gym_id: str) -> list[str]:
    return [w.id for w in db.query(Wall).filter(Wall.gym_id == gym_id).all()]


def _get_route_for_gym(db: Session, route_id: str, gym_id: str) -> Route:
    route = (
        db.query(Route)
        .options(joinedload(Route.wall), joinedload(Route.setters))
        .filter(Route.id == route_id)
        .first()
    )
    if not route or not route.wall or route.wall.gym_id != gym_id:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.get("", response_model=RouteListOut, summary="List / filter routes")
def list_routes(
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
    status: str | None = None,
    wall_id: str | None = None,
    zone: str | None = None,
    grade: str | None = None,
    style: str | None = None,
    setter_id: str | None = None,
    include_archived: bool = False,
    q: str | None = Query(default=None, description="Search color identifier or notes"),
):
    wall_ids = _gym_walls(db, gym.id)
    query = (
        db.query(Route)
        .options(joinedload(Route.wall), joinedload(Route.setters))
        .filter(Route.wall_id.in_(wall_ids))
    )
    if status:
        query = query.filter(Route.status == status)
    elif not include_archived:
        query = query.filter(Route.status != "archived")
    if wall_id:
        query = query.filter(Route.wall_id == wall_id)
    if grade:
        query = query.filter(Route.assigned_grade == grade)
    if zone:
        query = query.join(Wall).filter(Wall.zone == zone)
    if style:
        query = query.filter(Route.styles.contains(style))
    if q:
        like = f"%{q}%"
        query = query.filter((Route.color_identifier.ilike(like)) | (Route.notes.ilike(like)))

    routes = query.order_by(Route.set_date.desc()).all()
    if setter_id:
        routes = [r for r in routes if any(s.id == setter_id for s in r.setters)]

    items = [route_to_detail(r, db) for r in routes]
    return RouteListOut(items=items, total=len(items))


@router.post("", response_model=RouteDetailOut, status_code=201, summary="Create a route")
def create_route(
    payload: RouteCreate,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    wall = db.query(Wall).filter(Wall.id == payload.wall_id, Wall.gym_id == gym.id).first()
    if not wall:
        raise HTTPException(status_code=400, detail="Invalid wall_id for demo gym")

    setters: list[StaffUser] = []
    if payload.setter_ids:
        setters = (
            db.query(StaffUser)
            .filter(StaffUser.id.in_(payload.setter_ids), StaffUser.gym_id == gym.id)
            .all()
        )
        if len(setters) != len(set(payload.setter_ids)):
            raise HTTPException(status_code=400, detail="One or more setter_ids invalid")

    route = Route(
        wall_id=payload.wall_id,
        photo_url=payload.photo_url,
        color_identifier=payload.color_identifier,
        assigned_grade=payload.assigned_grade,
        grade_system=payload.grade_system,
        styles=",".join(payload.styles),
        status=payload.status,
        set_date=payload.set_date,
        reset_date=payload.reset_date,
        notes=payload.notes,
    )
    route.setters = setters
    db.add(route)
    db.commit()
    db.refresh(route)
    route = _get_route_for_gym(db, route.id, gym.id)
    return route_to_detail(route, db)


@router.get("/{route_id}", response_model=RouteDetailOut)
def get_route(
    route_id: str,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    route = _get_route_for_gym(db, route_id, gym.id)
    return route_to_detail(route, db)


@router.patch("/{route_id}", response_model=RouteDetailOut)
def update_route(
    route_id: str,
    payload: RouteUpdate,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    route = _get_route_for_gym(db, route_id, gym.id)
    data = payload.model_dump(exclude_unset=True)
    if "styles" in data and data["styles"] is not None:
        data["styles"] = ",".join(data["styles"])
    setter_ids = data.pop("setter_ids", None)
    if "wall_id" in data:
        wall = db.query(Wall).filter(Wall.id == data["wall_id"], Wall.gym_id == gym.id).first()
        if not wall:
            raise HTTPException(status_code=400, detail="Invalid wall_id")
    for k, v in data.items():
        setattr(route, k, v)
    if setter_ids is not None:
        setters = (
            db.query(StaffUser)
            .filter(StaffUser.id.in_(setter_ids), StaffUser.gym_id == gym.id)
            .all()
        )
        route.setters = setters
    route.updated_at = datetime.utcnow()
    db.commit()
    route = _get_route_for_gym(db, route_id, gym.id)
    return route_to_detail(route, db)


@router.patch("/{route_id}/status", response_model=RouteDetailOut)
def update_status(
    route_id: str,
    payload: RouteStatusUpdate,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    route = _get_route_for_gym(db, route_id, gym.id)
    route.status = payload.status
    route.updated_at = datetime.utcnow()
    db.commit()
    route = _get_route_for_gym(db, route_id, gym.id)
    return route_to_detail(route, db)
