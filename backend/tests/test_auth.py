from fastapi.testclient import TestClient


def test_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_gym_open_without_auth(client: TestClient):
    res = client.get("/api/v1/gym")
    assert res.status_code == 200
    assert res.json()["name"] == "Summit Lab Climbing"


def test_seed_status_shows_gym_without_routes(client: TestClient):
    res = client.get("/api/v1/seed-status")
    assert res.status_code == 200
    body = res.json()
    assert body["gyms"] >= 1
    assert body["walls"] >= 1
    assert body["routes"] == 0
    assert body["gym_name"] == "Summit Lab Climbing"
