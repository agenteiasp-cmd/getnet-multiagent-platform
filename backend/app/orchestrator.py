import time
from dataclasses import dataclass
from typing import Protocol

from openai import AsyncOpenAI

from app.agents.router import RouterAgent
from app.guardrails.pipeline import REFUSAL_MESSAGE, run_guardrails
from app.models.pipeline import AgentResult, UsageRecord
from app.observability.trace import new_trace_id


class SpecialistAgent(Protocol):
    async def handle(self, message: str, user_id: str) -> AgentResult: ...


class ObservabilityRecorderProtocol(Protocol):
    def record_chat(self, **kwargs) -> None: ...


@dataclass
class ChatOutcome:
    trace_id: str
    result: AgentResult
    usage: list[UsageRecord]


class Orchestrator:
    """Ties guardrails -> Router -> specialist dispatch together behind a
    single entry point, so POST /chat (section 8) is a thin adapter over
    this class. Every step's UsageRecord is collected into ChatOutcome.usage
    and, when a recorder is configured, persisted for the observability
    read APIs (section 10)."""

    def __init__(
        self,
        openai_client: AsyncOpenAI,
        router: RouterAgent,
        knowledge_agent: SpecialistAgent,
        support_agent: SpecialistAgent,
        escalation_agent: SpecialistAgent,
        recorder: ObservabilityRecorderProtocol | None = None,
    ):
        self._client = openai_client
        self._router = router
        self._specialists: dict[str, SpecialistAgent] = {
            "knowledge": knowledge_agent,
            "support": support_agent,
            "escalation": escalation_agent,
        }
        self._recorder = recorder

    async def handle_chat(self, message: str, user_id: str) -> ChatOutcome:
        trace_id = new_trace_id()

        start = time.perf_counter()
        guardrail_result = await run_guardrails(message, self._client)
        guardrail_latency_ms = (time.perf_counter() - start) * 1000
        guardrail_usage = UsageRecord(
            step="guardrails.check",
            model=None,
            input_data=message,
            output_data={"blocked": guardrail_result.blocked, "reason": guardrail_result.reason},
            latency_ms=guardrail_latency_ms,
            status="blocked" if guardrail_result.blocked else "ok",
        )

        if guardrail_result.blocked:
            result = AgentResult(
                response=REFUSAL_MESSAGE,
                agent_used="guardrails",
                intent="blocked",
                sources=[],
                tools_used=[],
            )
            outcome = ChatOutcome(trace_id=trace_id, result=result, usage=[guardrail_usage])
            self._record(outcome, message, user_id, status="blocked")
            return outcome

        router_outcome = await self._router.route(message)
        if router_outcome.result is not None:
            outcome = ChatOutcome(
                trace_id=trace_id,
                result=router_outcome.result,
                usage=[guardrail_usage, *router_outcome.usage],
            )
            self._record(outcome, message, user_id, status="ok")
            return outcome

        specialist = self._specialists[router_outcome.intent]
        result = await specialist.handle(message, user_id)
        outcome = ChatOutcome(
            trace_id=trace_id,
            result=result,
            usage=[guardrail_usage, *router_outcome.usage, *result.usage],
        )
        self._record(outcome, message, user_id, status="ok")
        return outcome

    def _record(self, outcome: ChatOutcome, message: str, user_id: str, status: str) -> None:
        if self._recorder is None:
            return
        self._recorder.record_chat(
            trace_id=outcome.trace_id,
            user_id=user_id,
            message=message,
            response=outcome.result.response,
            agent_used=outcome.result.agent_used,
            intent=outcome.result.intent,
            status=status,
            usage=outcome.usage,
        )
