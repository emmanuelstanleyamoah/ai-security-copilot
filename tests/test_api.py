from fastapi.testclient import TestClient

from backend.api import app


def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_investigate_endpoint():
    response = TestClient(app).post(
        "/investigate",
        json={"alert": "Privileged valid account signed in after impossible travel."},
    )
    assert response.status_code == 200
    body = response.json()
    assert "T1078" in body["technique_ids"]
    assert body["steps"]
