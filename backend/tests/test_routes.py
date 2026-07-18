from datetime import date

from fastapi.testclient import TestClient


def test_list_routes_empty_then_create(client: TestClient):
    empty = client.get("/api/v1/routes")
    assert empty.status_code == 200
    assert empty.json()["total"] == 0


def test_list_routes_and_filters(client: TestClient, sample_route: dict):
    res = client.get("/api/v1/routes")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1
    yellow = next(i for i in body["items"] if i["color_identifier"] == "Yellow")
    assert yellow["assigned_grade"] == "V3"
    assert len(yellow["holds"]) >= 1
    assert yellow["cells"] == [h["cell_index"] for h in yellow["holds"]]
    assert yellow["wall_key"]

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
            "name": "Teal Traverse",
            "color_identifier": "Teal",
            "display_color": "#14b8a6",
            "assigned_grade": "V2",
            "styles": ["slab", "fun"],
            "set_date": date.today().isoformat(),
            "setter_ids": [setter_id],
            "photo_url": "https://placehold.co/400x600/png?text=Teal",
            "holds": [
                {"sequence_index": 0, "row": 9, "col": 0, "hold_type": "jug", "notes": "start"},
                {"sequence_index": 1, "row": 8, "col": 1, "hold_type": "crimp"},
                {"sequence_index": 2, "row": 7, "col": 2, "hold_type": "pinch", "notes": "finish"},
            ],
        },
    )
    assert created.status_code == 201, created.text
    route_id = created.json()["id"]
    assert created.json()["styles"] == ["slab", "fun"]
    assert created.json()["setters"][0]["id"] == setter_id
    assert len(created.json()["holds"]) == 3
    assert created.json()["cells"] == [72, 65, 58]

    status = client.patch(
        f"/api/v1/routes/{route_id}/status",
        json={"status": "needs_review"},
    )
    assert status.status_code == 200
    assert status.json()["status"] == "needs_review"


def test_route_from_image_fallback(client: TestClient):
    walls = client.get("/api/v1/walls").json()
    wall_id = walls[0]["id"]
    # minimal 1x1 png
    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    res = client.post(
        "/api/v1/routes/from-image",
        data={"wall_id": wall_id, "color_identifier": "Teal"},
        files={"image": ("route.png", png, "image/png")},
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["color_identifier"] == "Teal"
    assert len(body["holds"]) >= 1
    assert body["cells"]


def test_route_detail(client: TestClient, sample_route: dict):
    detail = client.get(f"/api/v1/routes/{sample_route['id']}")
    assert detail.status_code == 200
    assert "health" in detail.json()
    assert "wall_name" in detail.json()
