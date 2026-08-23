from fastapi.testclient import TestClient

from app.dependencies import get_orchestrator
from app.main import app
from app.models.pipeline import AgentResult
from app.orchestrator import ChatOutcome


class FakeOrchestrator:
    def __init__(self, outcome: ChatOutcome):
        self._outcome = outcome
        self.calls: list[tuple[str, str]] = []

    async def handle_chat(self, message: str, user_id: str) -> ChatOutcome:
        self.calls.append((message, user_id))
        return self._outcome


def _override(outcome: ChatOutcome):
    fake = FakeOrchestrator(outcome)

    def _get():
        return fake

    return fake, _get


def test_missing_message_is_rejected():
    client = TestClient(app)
    response = client.post("/chat", json={"user_id": "user-1"})
    assert response.status_code == 422


def test_missing_user_id_is_rejected():
    client = TestClient(app)
    response = client.post("/chat", json={"message": "oi"})
    assert response.status_code == 422


def test_valid_request_returns_full_envelope():
    outcome = ChatOutcome(
        trace_id="trace-123",
        result=AgentResult(
            response="Olá! Como posso ajudar?",
            agent_used="router",
            intent="chitchat",
            sources=[],
            tools_used=["classify_intent"],
        ),
        usage=[],
    )
    fake, override = _override(outcome)
    app.dependency_overrides[get_orchestrator] = override
    try:
        client = TestClient(app)
        response = client.post("/chat", json={"message": "oi", "user_id": "user-1"})
        assert response.status_code == 200
        body = response.json()
        assert body == {
            "response": "Olá! Como posso ajudar?",
            "agent_used": "router",
            "intent": "chitchat",
            "sources": [],
            "tools_used": ["classify_intent"],
            "trace_id": "trace-123",
        }
        assert fake.calls == [("oi", "user-1")]
    finally:
        app.dependency_overrides.pop(get_orchestrator, None)


def test_response_fields_are_consistent_with_the_path_taken():
    outcome = ChatOutcome(
        trace_id="trace-456",
        result=AgentResult(
            response="A Get Clássica...",
            agent_used="knowledge",
            intent="knowledge",
            sources=[{"url": "https://site.getnet.com.br/maquininha/get-classica/", "title": "get-classica"}],
            tools_used=["pinecone_retrieval"],
        ),
        usage=[],
    )
    _, override = _override(outcome)
    app.dependency_overrides[get_orchestrator] = override
    try:
        client = TestClient(app)
        response = client.post(
            "/chat", json={"message": "qual a diferença entre Get Clássica e Get Smart?", "user_id": "user-1"}
        )
        body = response.json()
        assert body["agent_used"] == "knowledge"
        assert body["intent"] == "knowledge"
        assert body["sources"]
        assert body["tools_used"] == ["pinecone_retrieval"]
        assert body["trace_id"] == "trace-456"
    finally:
        app.dependency_overrides.pop(get_orchestrator, None)
