from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_demo_gym
from app.models.gym import Gym, Wall
from app.schemas import GymOut, WallCreate, WallOut

router = APIRouter(tags=["Gym & Walls"])


@router.get("/gym", response_model=GymOut, summary="Demo gym")
def get_gym(gym: Annotated[Gym, Depends(get_demo_gym)]):
    return gym


@router.get("/walls", response_model=list[WallOut])
def list_walls(
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = True,
):
    q = db.query(Wall).filter(Wall.gym_id == gym.id)
    if active_only:
        q = q.filter(Wall.is_active.is_(True))
    return q.order_by(Wall.name).all()


@router.post("/walls", response_model=WallOut, status_code=201)
def create_wall(
    payload: WallCreate,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    wall = Wall(gym_id=gym.id, **payload.model_dump())
    db.add(wall)
    db.commit()
    db.refresh(wall)
    return wall
