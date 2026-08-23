from unittest.mock import AsyncMock, MagicMock

from app.models.pipeline import AgentResult
from app.observability.jsonl_logger import JsonlLogger
from app.observability.models import StepRecord
from app.observability.recorder import ObservabilityRecorder
from app.observability.store import ObservabilityStore
from app.orchestrator import Orchestrator


def _step_record(step: str, trace_id: str = "trace-1") -> StepRecord:
    return StepRecord(
        trace_id=trace_id,
        conversation_id=trace_id,
        step=step,
        timestamp="2026-08-23T12:00:00+00:00",
        input="in",
        output="out",
        model="gpt-4o-mini",
        prompt_tokens=10,
        completion_tokens=5,
        latency_ms=12.3,
        status="ok",
    )


def test_jsonl_logger_appends_one_line_per_step(tmp_path):
    logger = JsonlLogger(tmp_path / "events.jsonl")

    for step in ["guardrails.check", "router.classify_intent", "knowledge.rag_generate"]:
        logger.append(_step_record(step))

    records = logger.read_all()
    assert [r["step"] for r in records] == [
        "guardrails.check",
        "router.classify_intent",
        "knowledge.rag_generate",
    ]


def test_sqlite_records_persist_across_a_fresh_connection(tmp_path):
    db_path = tmp_path / "observability.db"

    store_a = ObservabilityStore(db_path)
    store_a.upsert_conversation(
        conversation_id="trace-1",
        trace_id="trace-1",
        user_id="user-1",
        message="oi",
        response="olá",
        agent_used="router",
        intent="chitchat",
        status="ok",
        created_at="2026-08-23T12:00:00+00:00",
    )
    store_a.insert_step(_step_record("router.classify_intent"))

    # Simulate a fresh process: brand new ObservabilityStore instance
    # pointed at the same file, no shared in-memory state with store_a.
    store_b = ObservabilityStore(db_path)
    conversation = store_b.get_conversation("trace-1")
    steps = store_b.get_steps("trace-1")

    assert conversation is not None
    assert conversation["user_id"] == "user-1"
    assert len(steps) == 1
    assert steps[0]["step"] == "router.classify_intent"


def test_recorder_writes_both_jsonl_and_sqlite(tmp_path):
    jsonl_logger = JsonlLogger(tmp_path / "events.jsonl")
    store = ObservabilityStore(tmp_path / "observability.db")
    recorder = ObservabilityRecorder(jsonl_logger, store)

    usage = [
        _to_usage_record("guardrails.check"),
        _to_usage_record("router.classify_intent"),
    ]
    recorder.record_chat(
        trace_id="trace-42",
        user_id="user-1",
        message="oi",
        response="olá!",
        agent_used="router",
        intent="chitchat",
        status="ok",
        usage=usage,
    )

    assert len(jsonl_logger.read_all()) == 2
    assert len(store.get_steps("trace-42")) == 2
    assert store.get_conversation("trace-42")["intent"] == "chitchat"


def _to_usage_record(step: str):
    from app.models.pipeline import UsageRecord

    return UsageRecord(step=step, model="gpt-4o-mini", input_data="in", output_data="out")


class FakeSpecialist:
    def __init__(self, name: str):
        self.name = name

    async def handle(self, message: str, user_id: str) -> AgentResult:
        from app.models.pipeline import UsageRecord

        return AgentResult(
            response=f"resposta de {self.name}",
            agent_used=self.name,
            intent=self.name,
            sources=[],
            tools_used=[f"{self.name}_tool"],
            usage=[UsageRecord(step=f"{self.name}.generate", model="gpt-4o-mini")],
        )


class FakeRouter:
    async def route(self, message: str):
        from app.agents.router import RouterOutcome
        from app.models.pipeline import UsageRecord

        return RouterOutcome(
            intent="knowledge",
            reasoning="test",
            result=None,
            usage=[UsageRecord(step="router.classify_intent", model="gpt-4o-mini")],
        )


def _clean_moderation_client():
    category_result = MagicMock()
    category_result.flagged = False
    category_result.categories.model_dump.return_value = {}
    response = MagicMock()
    response.results = [category_result]
    client = MagicMock()
    client.moderations.create = AsyncMock(return_value=response)
    return client


async def test_single_chat_call_produces_coherent_multi_step_trace(tmp_path):
    jsonl_logger = JsonlLogger(tmp_path / "events.jsonl")
    store = ObservabilityStore(tmp_path / "observability.db")
    recorder = ObservabilityRecorder(jsonl_logger, store)

    orchestrator = Orchestrator(
        openai_client=_clean_moderation_client(),
        router=FakeRouter(),
        knowledge_agent=FakeSpecialist("knowledge"),
        support_agent=FakeSpecialist("support"),
        escalation_agent=FakeSpecialist("escalation"),
        recorder=recorder,
    )

    outcome = await orchestrator.handle_chat("qual a diferença entre Get Clássica e Get Smart?", "user-1")

    steps = store.get_steps(outcome.trace_id)
    step_names = [s["step"] for s in steps]
    assert step_names == ["guardrails.check", "router.classify_intent", "knowledge.generate"]
    assert all(s["trace_id"] == outcome.trace_id for s in steps)
    assert all(s["conversation_id"] == outcome.trace_id for s in steps)

    conversation = store.get_conversation(outcome.trace_id)
    assert conversation["agent_used"] == "knowledge"
    assert conversation["status"] == "ok"
