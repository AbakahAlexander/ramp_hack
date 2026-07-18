from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_demo_gym
from app.models.gym import Gym
from app.models.user import StaffUser
from app.schemas import StaffUserOut

router = APIRouter(prefix="/staff", tags=["Staff"])


@router.get(
    "",
    response_model=list[StaffUserOut],
    summary="List staff / setters",
    response_description="Staff profiles for the demo gym",
    description=(
        "List staff members. Pass `setters_only=true` to get IDs for `setter_ids` when creating a route."
    ),
)
def list_staff(
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
    setters_only: bool = False,
):
    q = db.query(StaffUser).filter(StaffUser.gym_id == gym.id, StaffUser.is_active.is_(True))
    if setters_only:
        q = q.filter(StaffUser.is_setter.is_(True))
    return q.order_by(StaffUser.full_name).all()
