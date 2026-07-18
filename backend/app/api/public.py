from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.gym import Gym
from app.models.route import Route
from app.schemas import PublicRouteCard

router = APIRouter(prefix="/public", tags=["Public (climber QR)"])


@router.get("/routes/{route_id}", response_model=PublicRouteCard, summary="Route card for QR / mobile flow")
def public_route_card(
    route_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    route = (
        db.query(Route)
        .options(joinedload(Route.wall))
        .filter(Route.id == route_id)
        .first()
    )
    if not route or not route.wall:
        raise HTTPException(status_code=404, detail="Route not found")
    if route.status == "archived":
        raise HTTPException(status_code=404, detail="Route not found")

    gym = db.query(Gym).filter(Gym.id == route.wall.gym_id).first()
    return PublicRouteCard(
        id=route.id,
        color_identifier=route.color_identifier,
        assigned_grade=route.assigned_grade,
        grade_system=route.grade_system,
        styles=route.style_list,
        wall_name=route.wall.name,
        zone=route.wall.zone,
        photo_url=route.photo_url,
        tag_vocabulary=gym.tag_vocabulary if gym else [],
        gym_name=gym.name if gym else "",
    )
