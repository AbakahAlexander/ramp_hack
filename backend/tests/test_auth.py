from fastapi.testclient import TestClient


def test_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_gym_open_without_auth(client: TestClient):
    res = client.get("/api/v1/gym")
    assert res.status_code == 200
    assert res.json()["name"] == "Summit Lab Climbing"
