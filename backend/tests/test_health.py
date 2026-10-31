from fastapi.testclient import TestClient

from app.main import app

# TestClient calls the app directly in memory — no running server needed.
client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
