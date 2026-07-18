"""Seed a demo gym so the frontend can demo the full feedback loop."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models.feedback import Feedback, IssueReport
from app.models.gym import Gym, Wall
from app.models.route import Route
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

# Demo credentials (document for frontend team)
DEMO_PASSWORD = "cruxdemo123"


def seed_if_empty(db: Session) -> dict | None:
    if db.query(Gym).first():
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
        Wall(gym_id=gym.id, name="Slab Wall", zone="Front", angle_type="slab"),
        Wall(gym_id=gym.id, name="Steep Wall", zone="Cave", angle_type="overhang"),
        Wall(gym_id=gym.id, name="Vertical Board", zone="Training", angle_type="vertical"),
    ]
    db.add_all(walls)
    db.flush()

    manager = StaffUser(
        gym_id=gym.id,
        email="manager@summitlab.demo",
        full_name="Alex Manager",
        hashed_password=hash_password(DEMO_PASSWORD),
        role="manager",
        is_setter=True,
    )
    setter_a = StaffUser(
        gym_id=gym.id,
        email="jordan@summitlab.demo",
        full_name="Jordan Setter",
        hashed_password=hash_password(DEMO_PASSWORD),
        role="setter",
        is_setter=True,
    )
    setter_b = StaffUser(
        gym_id=gym.id,
        email="sam@summitlab.demo",
        full_name="Sam Setter",
        hashed_password=hash_password(DEMO_PASSWORD),
        role="setter",
        is_setter=True,
    )
    floor = StaffUser(
        gym_id=gym.id,
        email="floor@summitlab.demo",
        full_name="Casey Floor",
        hashed_password=hash_password(DEMO_PASSWORD),
        role="floor",
        is_setter=False,
    )
    db.add_all([manager, setter_a, setter_b, floor])
    db.flush()

    today = date.today()
    routes = [
        Route(
            wall_id=walls[0].id,
            color_identifier="Yellow",
            assigned_grade="V3",
            styles="slab,technical",
            status="active",
            set_date=today - timedelta(days=5),
            photo_url="https://placehold.co/400x600/png?text=Yellow+V3",
            notes="Demo narrative route — expect reachy feedback",
        ),
        Route(
            wall_id=walls[0].id,
            color_identifier="Green",
            assigned_grade="V1",
            styles="slab",
            status="active",
            set_date=today - timedelta(days=20),
            photo_url="https://placehold.co/400x600/png?text=Green+V1",
        ),
        Route(
            wall_id=walls[1].id,
            color_identifier="Red",
            assigned_grade="V5",
            styles="overhang,powerful",
            status="needs_review",
            set_date=today - timedelta(days=35),
            reset_date=today + timedelta(days=7),
            photo_url="https://placehold.co/400x600/png?text=Red+V5",
            notes="Sharp holds reported",
        ),
        Route(
            wall_id=walls[1].id,
            color_identifier="Blue",
            assigned_grade="V7",
            styles="overhang,coordination",
            status="active",
            set_date=today - timedelta(days=12),
            photo_url="https://placehold.co/400x600/png?text=Blue+V7",
        ),
        Route(
            wall_id=walls[2].id,
            color_identifier="Purple",
            assigned_grade="V4",
            styles="technical,compression",
            status="scheduled_for_strip",
            set_date=today - timedelta(days=45),
            reset_date=today + timedelta(days=3),
            photo_url="https://placehold.co/400x600/png?text=Purple+V4",
        ),
        Route(
            wall_id=walls[2].id,
            color_identifier="Orange",
            assigned_grade="V2",
            styles="fun",
            status="active",
            set_date=today - timedelta(days=8),
            photo_url="https://placehold.co/400x600/png?text=Orange+V2",
        ),
    ]
    routes[0].setters = [setter_a]
    routes[1].setters = [setter_b]
    routes[2].setters = [setter_a, manager]
    routes[3].setters = [setter_b]
    routes[4].setters = [setter_a]
    routes[5].setters = [setter_b]
    db.add_all(routes)
    db.flush()

    # Feedback on yellow V3 — grade feels harder / reachy (demo narrative)
    yellow = routes[0]
    for i, (outcome, grade, enjoyment, tags, days_ago) in enumerate(
        [
            ("sent", "V4", 4, "technical,reachy", 1),
            ("tried", "V4", 3, "reachy,morpho", 2),
            ("sent", "V3", 5, "technical,great movement", 2),
            ("projecting", "V5", 3, "reachy,confusing", 3),
            ("sent", "V4", 4, "technical,reachy", 4),
            ("tried", "V4", 2, "reachy", 5),
        ]
    ):
        db.add(
            Feedback(
                route_id=yellow.id,
                outcome=outcome,
                perceived_grade=grade,
                enjoyment=enjoyment,
                tags=tags,
                comment="Felt taller-friendly" if "reachy" in tags else None,
                contributor_id=f"anon-yellow-{i}",
                created_at=datetime.utcnow() - timedelta(days=days_ago),
            )
        )

    # Declining engagement + sharp issue on red V5
    red = routes[2]
    for i in range(8):
        db.add(
            Feedback(
                route_id=red.id,
                outcome="sent" if i % 2 == 0 else "tried",
                perceived_grade="V5",
                enjoyment=3,
                tags="powerful,sharp" if i < 3 else "powerful",
                contributor_id=f"anon-red-{i}",
                created_at=datetime.utcnow() - timedelta(days=20 - i),
            )
        )
    db.add(
        IssueReport(
            route_id=red.id,
            issue_type="sharp",
            note="Finishing hold feels razor sharp",
            status="open",
        )
    )

    # Healthy orange route
    orange = routes[5]
    for i in range(4):
        db.add(
            Feedback(
                route_id=orange.id,
                outcome="sent",
                perceived_grade="V2",
                enjoyment=5,
                tags="fun,great movement",
                contributor_id=f"anon-orange-{i}",
                created_at=datetime.utcnow() - timedelta(days=i),
            )
        )

    db.commit()
    return {
        "gym_id": gym.id,
        "gym_name": gym.name,
        "demo_users": [
            {"email": "manager@summitlab.demo", "password": DEMO_PASSWORD, "role": "manager"},
            {"email": "jordan@summitlab.demo", "password": DEMO_PASSWORD, "role": "setter"},
            {"email": "sam@summitlab.demo", "password": DEMO_PASSWORD, "role": "setter"},
            {"email": "floor@summitlab.demo", "password": DEMO_PASSWORD, "role": "floor"},
        ],
        "highlight_route_id": yellow.id,
    }
