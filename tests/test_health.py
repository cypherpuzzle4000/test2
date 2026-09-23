from fastapi.testclient import TestClient

from app.main import app


def test_liveness_contract() -> None:
    client = TestClient(app)
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_invalid_task_is_rejected() -> None:
    client = TestClient(app)
    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422