from fastapi.testclient import TestClient


def test_public_route_card_and_feedback_loop(client: TestClient, sample_route: dict):
    route_id = sample_route["id"]

    card = client.get(f"/api/v1/public/routes/{route_id}")
    assert card.status_code == 200
    assert card.json()["assigned_grade"] == "V3"
    assert len(card.json()["tag_vocabulary"]) > 0

    fb = client.post(
        f"/api/v1/public/routes/{route_id}/feedback",
        json={
            "outcome": "sent",
            "perceived_grade": "V4",
            "enjoyment": 4,
            "tags": ["technical", "reachy"],
            "comment": "Long moves on the crux",
        },
    )
    assert fb.status_code == 201, fb.text
    assert fb.json()["outcome"] == "sent"

    sharp = client.post(
        f"/api/v1/public/routes/{route_id}/feedback",
        json={"outcome": "tried", "tags": ["sharp"], "enjoyment": 2},
    )
    assert sharp.status_code == 201

    issues = client.get("/api/v1/issues?route_id=" + route_id)
    assert issues.status_code == 200
    assert any(i["issue_type"] == "sharp" for i in issues.json())

    staff_fb = client.get(f"/api/v1/routes/{route_id}/feedback")
    assert staff_fb.status_code == 200
    assert len(staff_fb.json()) >= 1


def test_dashboard_endpoints(client: TestClient, sample_route: dict):
    # add an issue so open_issue_count can be > 0
    client.post(
        f"/api/v1/issues/routes/{sample_route['id']}",
        json={"issue_type": "sharp", "note": "test"},
    )

    overview = client.get("/api/v1/dashboard/overview")
    assert overview.status_code == 200
    data = overview.json()
    assert "wall_health" in data
    assert "routes_needing_review" in data
    assert data["open_issue_count"] >= 1

    reset = client.get("/api/v1/dashboard/reset-queue")
    assert reset.status_code == 200
    assert len(reset.json()) >= 1

    coverage = client.get("/api/v1/dashboard/coverage")
    assert coverage.status_code == 200
    assert "cells" in coverage.json()

    insights = client.get("/api/v1/dashboard/setter-insights")
    assert insights.status_code == 200
