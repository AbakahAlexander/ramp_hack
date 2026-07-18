import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SEED_ON_STARTUP"] = "false"
os.environ["CLEAR_ROUTES_ON_STARTUP"] = "false"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["OPENAI_API_KEY"] = ""

from app.database import Base, get_db  # noqa: E402
from app.main import create_app  # noqa: E402
from app.services.seed import seed_if_empty  # noqa: E402


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    seed_if_empty(db)
    db.close()

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    application = create_app()
    application.dependency_overrides[get_db] = override_get_db
    with TestClient(application) as c:
        yield c
    application.dependency_overrides.clear()


@pytest.fixture()
def sample_route(client: TestClient) -> dict:
    walls = client.get("/api/v1/walls").json()
    wall_id = walls[0]["id"]
    created = client.post(
        "/api/v1/routes",
        json={
            "wall_id": wall_id,
            "name": "Reach Check",
            "color_identifier": "Yellow",
            "display_color": "#e8c84a",
            "assigned_grade": "V3",
            "styles": ["slab", "technical"],
            "set_date": "2026-07-13",
            "holds": [
                {"sequence_index": 0, "row": 9, "col": 0, "hold_type": "jug"},
                {"sequence_index": 1, "row": 8, "col": 1, "hold_type": "crimp"},
                {"sequence_index": 2, "row": 7, "col": 1, "hold_type": "pinch"},
            ],
        },
    )
    assert created.status_code == 201, created.text
    return created.json()
