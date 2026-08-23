import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_observability_store
from app.main import app
from app.observability.store import ObservabilityStore


@pytest.fixture
def store(tmp_path):
    s = ObservabilityStore(tmp_path / "observability.db")
    app.dependency_overrides[get_observability_store] = lambda: s
    yield s
    app.dependency_overrides.pop(get_observability_store, None)


def test_submitted_feedback_is_persisted(store):
    client = TestClient(app)
    response = client.post(
        "/feedback", json={"trace_id": "trace-1", "agent_used": "knowledge", "rating": 1}
    )
    assert response.status_code == 200

    aggregates = store.agent_feedback()
    assert aggregates["knowledge"]["total"] == 1
    assert aggregates["knowledge"]["positive_rate"] == 1.0


def test_feedback_survives_a_fresh_store_instance(tmp_path):
    db_path = tmp_path / "observability.db"
    store_a = ObservabilityStore(db_path)
    store_a.insert_feedback(
        trace_id="trace-2", agent_used="support", rating=-1, created_at="2026-08-23T10:00:00+00:00"
    )

    store_b = ObservabilityStore(db_path)
    aggregates = store_b.agent_feedback()
    assert aggregates["support"]["total"] == 1
    assert aggregates["support"]["positive_rate"] == 0.0
    assert aggregates["support"]["avg_score"] == -1.0


def test_get_agents_feedback_returns_aggregates(store):
    client = TestClient(app)
    client.post("/feedback", json={"trace_id": "t1", "agent_used": "knowledge", "rating": 1})
    client.post("/feedback", json={"trace_id": "t2", "agent_used": "knowledge", "rating": -1})
    client.post("/feedback", json={"trace_id": "t3", "agent_used": "support", "rating": 1})

    response = client.get("/agents/feedback")
    body = response.json()

    assert body["knowledge"]["total"] == 2
    assert body["knowledge"]["positive_rate"] == 0.5
    assert body["support"]["positive_rate"] == 1.0
