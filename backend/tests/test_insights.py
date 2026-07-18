from fastapi.testclient import TestClient

SAMPLE_FEEDBACK = """
Yellow V3 on the slab felt super reachy and sandbagged — taller climbers only.
Red cave route has a sharp finishing hold, please fix or strip.
Orange V2 is a blast, please keep it forever.
Purple board climb is tired and boring after weeks.
"""


def test_analyze_insights_fallback(client: TestClient):
    routes = client.get("/api/v1/routes").json()["items"]
    # Use FE-shaped catalog built from seed names isn't required — send static ids
    catalog = [
        {
            "id": "r-102",
            "name": "Reach Check",
            "grade": "V3",
            "wall": "Slab Wall",
            "colorName": "Yellow",
            "style": "Technical",
            "status": "Review",
        },
        {
            "id": "r-103",
            "name": "Cave Crusher",
            "grade": "V5",
            "wall": "Steep Wall",
            "colorName": "Red",
            "style": "Powerful",
            "status": "Review",
        },
        {
            "id": "r-105",
            "name": "Board Meeting",
            "grade": "V2",
            "wall": "Vertical Board",
            "colorName": "Orange",
            "style": "Fun",
            "status": "Healthy",
        },
        {
            "id": "r-106",
            "name": "Purple Rain",
            "grade": "V4",
            "wall": "Vertical Board",
            "colorName": "Purple",
            "style": "Compression",
            "status": "Strip soon",
        },
    ]
    res = client.post(
        "/api/v1/insights/analyze",
        json={"feedback_text": SAMPLE_FEEDBACK, "routes": catalog},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["gym_summary"]
    assert len(body["routes"]) == 4
    by_id = {r["route_id"]: r for r in body["routes"]}
    assert by_id["r-102"]["recommendation"] in ("keep", "monitor", "change_out")
    assert by_id["r-105"]["recommendation"] == "keep"
    assert by_id["r-103"]["recommendation"] == "change_out"

    latest = client.get("/api/v1/insights/latest")
    assert latest.status_code == 200
    assert "r-102" in latest.json()["routes"]

    one = client.get("/api/v1/insights/routes/r-102")
    assert one.status_code == 200
    assert one.json()["route_id"] == "r-102"
