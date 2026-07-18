from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_demo_gym
from app.models.feedback import Feedback, IssueReport
from app.models.gym import Gym, Wall
from app.models.route import Route
from app.models.user import StaffUser
from app.schemas import GymOut, SeedStatusOut, WallCreate, WallOut

router = APIRouter(tags=["Gym & Walls"])


@router.get(
    "/gym",
    response_model=GymOut,
    summary="Get the demo gym",
    response_description="Gym profile including grade system and feedback tag vocabulary",
    description=(
        "Returns the seeded demo gym (Summit Lab Climbing). "
        "Use `tag_vocabulary` to populate climber feedback tag chips."
    ),
)
def get_gym(gym: Annotated[Gym, Depends(get_demo_gym)]):
    return gym


@router.get(
    "/walls",
    response_model=list[WallOut],
    summary="List walls",
    response_description="Walls in the demo gym",
    description="List climbing walls. Use a wall `id` when creating routes.",
)
def list_walls(
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = True,
):
    q = db.query(Wall).filter(Wall.gym_id == gym.id)
    if active_only:
        q = q.filter(Wall.is_active.is_(True))
    return q.order_by(Wall.name).all()


@router.post(
    "/walls",
    response_model=WallOut,
    status_code=201,
    summary="Create a wall",
    response_description="The created wall",
    description="Add a new wall/section to the demo gym.",
)
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


@router.get(
    "/seed-status",
    response_model=SeedStatusOut,
    summary="Check whether demo DB data is loaded",
    response_description="Counts of seeded entities",
    description=(
        "Quick sanity check that the database has demo gym, walls, routes, feedback, and issues. "
        "On startup, empty databases are auto-seeded when `SEED_ON_STARTUP=true`."
    ),
    tags=["Meta"],
)
def seed_status(db: Annotated[Session, Depends(get_db)]):
    gym = db.query(Gym).first()
    gyms = db.query(Gym).count()
    walls = db.query(Wall).count()
    routes = db.query(Route).count()
    staff = db.query(StaffUser).count()
    feedback = db.query(Feedback).count()
    issues = db.query(IssueReport).count()
    seeded = gyms > 0 and routes > 0
    return SeedStatusOut(
        gym_name=gym.name if gym else None,
        gyms=gyms,
        walls=walls,
        routes=routes,
        staff=staff,
        feedback=feedback,
        issues=issues,
        seeded=seeded,
        hint=(
            "GET /api/v1/dashboard/overview"
            if seeded
            else "Restart with SEED_ON_STARTUP=true or redeploy the service"
        ),
    )
