"""Shared dependencies — hackathon MVP has no auth; use the seeded demo gym."""

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.gym import Gym


def get_demo_gym(db: Annotated[Session, Depends(get_db)]) -> Gym:
    gym = db.query(Gym).first()
    if not gym:
        raise HTTPException(status_code=503, detail="No gym seeded yet")
    return gym
