"""Seed gym + walls + staff only. Routes are added via Add Route (image → AI grid)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models.feedback import Feedback, IssueReport
from app.models.gym import Gym, Wall
from app.models.route import Route, RouteHold
from app.models.user import StaffUser

DEFAULT_TAGS = [
    "fun",
    "technical",
    "powerful",
    "reachy",
    "morpho",
    "confusing",
    "sharp",
    "sandbagged",
    "soft",
    "great movement",
]

DEMO_PASSWORD = "cruxdemo123"


def build_holds_for_wall(wall: Wall, hold_inputs: list) -> list[RouteHold]:
    cols = wall.grid_cols or 8
    rows = wall.grid_rows or 10
    holds: list[RouteHold] = []
    for item in hold_inputs:
        data = item.model_dump() if hasattr(item, "model_dump") else dict(item)

        if data.get("x") is not None and data.get("y") is not None:
            x = float(data["x"])
            y = float(data["y"])
            if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
                raise ValueError(f"Hold x/y must be in [0,1], got ({x},{y})")
            row = int(round(y * (rows - 1)))
            col = int(round(x * (cols - 1)))
        elif data.get("row") is not None and data.get("col") is not None:
            row = int(data["row"])
            col = int(data["col"])
            if row < 0 or col < 0 or row >= rows or col >= cols:
                raise ValueError(f"Hold ({row},{col}) outside wall grid {cols}x{rows}")
            x = (col + 0.5) / cols
            y = (row + 0.5) / rows
        else:
            raise ValueError("Each hold needs x/y (preferred) or row/col")

        size = float(data.get("size") or 0.05)
        size = max(0.01, min(0.5, size))
        cell = data.get("cell_index")
        if cell is None:
            cell = row * cols + col
        holds.append(
            RouteHold(
                sequence_index=int(data["sequence_index"]),
                cell_index=int(cell),
                row=row,
                col=col,
                x=x,
                y=y,
                size=size,
                hold_type=data.get("hold_type") or "other",
                notes=data.get("notes"),
            )
        )
    holds.sort(key=lambda h: h.sequence_index)
    return holds


def clear_all_routes(db: Session) -> int:
    """Remove every route (and cascaded holds/feedback/issues)."""
    routes = db.query(Route).all()
    count = len(routes)
    for route in routes:
        db.delete(route)
    if count:
        db.commit()
    return count


def seed_if_empty(db: Session) -> dict | None:
    """Ensure gym/walls/staff exist. Never seeds routes."""
    existing = db.query(Gym).first()
    if existing:
        _ensure_wall_geometry(db)
        return None

    gym = Gym(
        name="Summit Lab Climbing",
        locations=["Main Street"],
        grade_system="V-scale",
        tag_vocabulary=DEFAULT_TAGS,
    )
    db.add(gym)
    db.flush()

    walls = [
        Wall(
            gym_id=gym.id,
            name="Slab Wall",
            zone="Front",
            angle_type="slab",
            wall_key="slab",
            grid_cols=8,
            grid_rows=10,
        ),
        Wall(
            gym_id=gym.id,
            name="Steep Wall",
            zone="Cave",
            angle_type="overhang",
            wall_key="steep",
            grid_cols=8,
            grid_rows=10,
        ),
        Wall(
            gym_id=gym.id,
            name="Vertical Board",
            zone="Training",
            angle_type="vertical",
            wall_key="vertical",
            grid_cols=8,
            grid_rows=10,
        ),
    ]
    db.add_all(walls)
    db.flush()

    db.add_all(
        [
            StaffUser(
                gym_id=gym.id,
                email="manager@summitlab.demo",
                full_name="Alex Manager",
                hashed_password=hash_password(DEMO_PASSWORD),
                role="manager",
                is_setter=True,
            ),
            StaffUser(
                gym_id=gym.id,
                email="jordan@summitlab.demo",
                full_name="Jordan Setter",
                hashed_password=hash_password(DEMO_PASSWORD),
                role="setter",
                is_setter=True,
            ),
            StaffUser(
                gym_id=gym.id,
                email="sam@summitlab.demo",
                full_name="Sam Setter",
                hashed_password=hash_password(DEMO_PASSWORD),
                role="setter",
                is_setter=True,
            ),
            StaffUser(
                gym_id=gym.id,
                email="floor@summitlab.demo",
                full_name="Casey Floor",
                hashed_password=hash_password(DEMO_PASSWORD),
                role="floor",
                is_setter=False,
            ),
        ]
    )
    db.commit()
    return {"gym_id": gym.id, "gym_name": gym.name, "routes_seeded": 0}


def _ensure_wall_geometry(db: Session) -> None:
    key_by_name = {
        "Slab Wall": ("slab", 8, 10),
        "Steep Wall": ("steep", 8, 10),
        "Vertical Board": ("vertical", 8, 10),
    }
    changed = False
    for wall in db.query(Wall).all():
        meta = key_by_name.get(wall.name)
        if meta and (not wall.wall_key or not wall.grid_cols):
            wall.wall_key, wall.grid_cols, wall.grid_rows = meta
            changed = True
    if changed:
        db.commit()
