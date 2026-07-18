from datetime import date

from fastapi.testclient import TestClient


def test_list_routes_and_filters(client: TestClient):
    res = client.get("/api/v1/routes")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 5
    assert all("health" in item for item in body["items"])

    yellow = next(i for i in body["items"] if i["color_identifier"] == "Yellow")
    assert yellow["assigned_grade"] == "V3"
    assert yellow["health"]["unique_contributors"] >= 1
    assert yellow["health"]["insight_quality"] in ("low", "medium", "high")

    filtered = client.get("/api/v1/routes?grade=V3")
    assert filtered.status_code == 200
    assert all(i["assigned_grade"] == "V3" for i in filtered.json()["items"])


def test_create_route_and_status_change(client: TestClient):
    walls = client.get("/api/v1/walls")
    assert walls.status_code == 200
    wall_id = walls.json()[0]["id"]

    staff = client.get("/api/v1/staff?setters_only=true")
    setter_id = staff.json()[0]["id"]

    created = client.post(
        "/api/v1/routes",
        json={
            "wall_id": wall_id,
            "color_identifier": "Teal",
            "assigned_grade": "V2",
            "styles": ["slab", "fun"],
            "set_date": date.today().isoformat(),
            "setter_ids": [setter_id],
            "photo_url": "https://placehold.co/400x600/png?text=Teal",
        },
    )
    assert created.status_code == 201, created.text
    route_id = created.json()["id"]
    assert created.json()["styles"] == ["slab", "fun"]
    assert created.json()["setters"][0]["id"] == setter_id

    status = client.patch(
        f"/api/v1/routes/{route_id}/status",
        json={"status": "needs_review"},
    )
    assert status.status_code == 200
    assert status.json()["status"] == "needs_review"


def test_route_detail(client: TestClient):
    routes = client.get("/api/v1/routes").json()["items"]
    route_id = routes[0]["id"]
    detail = client.get(f"/api/v1/routes/{route_id}")
    assert detail.status_code == 200
    assert "health" in detail.json()
    assert "wall_name" in detail.json()
