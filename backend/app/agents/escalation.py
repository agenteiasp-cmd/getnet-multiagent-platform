import time
from typing import Awaitable, Callable

from app.models.pipeline import AgentResult, UsageRecord
from app.tools.escalation_tool import HandoffConfirmation, default_mock_handoff_call

HANDOFF_TOOL_NAME = "mock_handoff_call"

HandoffCall = Callable[[str, str], Awaitable[HandoffConfirmation]]


class EscalationAgent:
    """Performs a mocked human-handoff call and confirms it to the user.
    The differentiator fourth agent for this challenge."""

    def __init__(self, handoff_call: HandoffCall = default_mock_handoff_call):
        self._handoff_call = handoff_call

    async def handle(self, message: str, user_id: str) -> AgentResult:
        start = time.perf_counter()
        confirmation = await self._handoff_call(message, user_id)
        latency_ms = (time.perf_counter() - start) * 1000

        response = (
            f"Encaminhei sua solicitação para um atendente humano. Seu protocolo é "
            f"{confirmation.ticket_id}, você está na posição {confirmation.queue_position} "
            f"da fila, com tempo estimado de espera de {confirmation.estimated_wait_minutes} minutos."
        )

        usage = [
            UsageRecord(
                step="escalation.mock_handoff_call",
                model=None,
                input_data={"message": message, "user_id": user_id},
                output_data={
                    "ticket_id": confirmation.ticket_id,
                    "queue_position": confirmation.queue_position,
                    "estimated_wait_minutes": confirmation.estimated_wait_minutes,
                },
                latency_ms=latency_ms,
            )
        ]

        return AgentResult(
            response=response,
            agent_used="escalation",
            intent="escalation",
            sources=[],
            tools_used=[HANDOFF_TOOL_NAME],
            usage=usage,
        )
