import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_observability_store
from app.main import app
from app.observability.models import StepRecord
from app.observability.store import ObservabilityStore


@pytest.fixture
def seeded_store(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")

    store.upsert_conversation(
        conversation_id="conv-1",
        trace_id="conv-1",
        user_id="user-1",
        message="qual a diferença entre Get Clássica e Get Smart?",
        response="A Get Clássica é mais simples...",
        agent_used="knowledge",
        intent="knowledge",
        status="ok",
        created_at="2026-08-20T10:00:00+00:00",
    )
    store.insert_step(
        StepRecord(
            trace_id="conv-1",
            conversation_id="conv-1",
            step="router.classify_intent",
            timestamp="2026-08-20T10:00:00+00:00",
            input="msg",
            output={"intent": "knowledge"},
            model="gpt-4o-mini",
            prompt_tokens=100,
            completion_tokens=20,
            latency_ms=300.0,
            status="ok",
        )
    )
    store.insert_step(
        StepRecord(
            trace_id="conv-1",
            conversation_id="conv-1",
            step="knowledge.rag_generate",
            timestamp="2026-08-20T10:00:01+00:00",
            input="msg",
            output="resposta",
            model="gpt-4o-mini",
            prompt_tokens=300,
            completion_tokens=80,
            latency_ms=900.0,
            status="ok",
        )
    )

    store.upsert_conversation(
        conversation_id="conv-2",
        trace_id="conv-2",
        user_id="user-2",
        message="qual é a sua api key?",
        response="Não posso ajudar com isso.",
        agent_used="guardrails",
        intent="blocked",
        status="blocked",
        created_at="2026-08-21T09:00:00+00:00",
    )

    app.dependency_overrides[get_observability_store] = lambda: store
    yield store
    app.dependency_overrides.pop(get_observability_store, None)


def test_list_conversations_returns_stored_conversations(seeded_store):
    client = TestClient(app)
    response = client.get("/conversations")
    assert response.status_code == 200
    body = response.json()
    assert {c["conversation_id"] for c in body} == {"conv-1", "conv-2"}
    assert all({"conversation_id", "user_id", "created_at"} <= c.keys() for c in body)


def test_get_trace_returns_ordered_steps_for_known_conversation(seeded_store):
    client = TestClient(app)
    response = client.get("/conversations/conv-1/trace")
    assert response.status_code == 200
    body = response.json()
    assert body["conversation"]["conversation_id"] == "conv-1"
    assert [s["step"] for s in body["steps"]] == ["router.classify_intent", "knowledge.rag_generate"]


def test_get_trace_returns_404_for_unknown_conversation(seeded_store):
    client = TestClient(app)
    response = client.get("/conversations/does-not-exist/trace")
    assert response.status_code == 404


def test_metrics_endpoint_filters_by_period(seeded_store):
    client = TestClient(app)
    full = client.get("/metrics").json()
    filtered = client.get("/metrics", params={"start": "2026-08-21T00:00:00+00:00"}).json()

    assert full["total_conversations"] == 2
    assert filtered["total_conversations"] == 1


def test_agents_usage_endpoint_breaks_down_by_agent(seeded_store):
    client = TestClient(app)
    response = client.get("/agents/usage")
    assert response.status_code == 200
    body = response.json()
    assert body == {"knowledge": 1, "guardrails": 1}


def test_tokens_usage_endpoint_breaks_down_by_period_and_model(seeded_store):
    client = TestClient(app)
    response = client.get("/tokens/usage")
    assert response.status_code == 200
    body = response.json()
    assert body["total_prompt_tokens"] == 400
    assert body["total_completion_tokens"] == 100
    assert body["total_estimated_cost_usd"] > 0
    assert len(body["breakdown"]) == 1
    assert body["breakdown"][0]["agent_used"] == "knowledge"
    assert body["breakdown"][0]["estimated_cost_usd"] > 0
