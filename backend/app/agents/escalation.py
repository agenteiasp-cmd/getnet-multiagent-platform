import re
import time
from typing import Awaitable, Callable

from app.models.pipeline import AgentResult, UsageRecord
from app.tools.escalation_tool import (
    HandoffConfirmation,
    PhoneTransferConfirmation,
    default_mock_handoff_call,
    default_mock_phone_transfer_call,
)

HANDOFF_TOOL_NAME = "mock_handoff_call"
PHONE_TRANSFER_TOOL_NAME = "mock_phone_transfer_call"

HandoffCall = Callable[[str, str], Awaitable[HandoffConfirmation]]
PhoneTransferCall = Callable[[str, str], Awaitable[PhoneTransferConfirmation]]

# A user asking to be escalated "by phone" wants to leave the chat entirely,
# not join the in-chat queue - matched on the request itself, not on intent
# classification, since 'escalation' only tells us "wants a human", not
# which channel.
PHONE_CALL_PATTERN = re.compile(
    r"\b(liga[çc][ãa]o|ligar|ligue|telefonar|telefone)\b",
    re.IGNORECASE,
)


class EscalationAgent:
    """Performs a mocked human-handoff call and confirms it to the user.
    The differentiator fourth agent for this challenge. Branches into two
    mocked flows: the default in-chat queue handoff, or - when the user
    asks to be escalated by phone - a phone transfer with a one-time code
    for Getnet's support line."""

    def __init__(
        self,
        handoff_call: HandoffCall = default_mock_handoff_call,
        phone_transfer_call: PhoneTransferCall = default_mock_phone_transfer_call,
    ):
        self._handoff_call = handoff_call
        self._phone_transfer_call = phone_transfer_call

    async def handle(self, message: str, user_id: str) -> AgentResult:
        if PHONE_CALL_PATTERN.search(message):
            return await self._handle_phone_transfer(message, user_id)
        return await self._handle_chat_handoff(message, user_id)

    async def _handle_phone_transfer(self, message: str, user_id: str) -> AgentResult:
        start = time.perf_counter()
        confirmation = await self._phone_transfer_call(message, user_id)
        latency_ms = (time.perf_counter() - start) * 1000

        response = (
            f"Sem problemas! Ligue para {confirmation.phone_number}, o 0800 da Getnet, "
            f"e quando o atendimento eletrônico pedir, informe o código {confirmation.access_code}. "
            f"Você será direcionado direto para um atendente especialista, sem precisar "
            f"repetir o que já me contou."
        )

        usage = [
            UsageRecord(
                step="escalation.mock_phone_transfer",
                model=None,
                input_data={"message": message, "user_id": user_id},
                output_data={
                    "phone_number": confirmation.phone_number,
                    "access_code": confirmation.access_code,
                },
                latency_ms=latency_ms,
            )
        ]

        return AgentResult(
            response=response,
            agent_used="escalation",
            intent="escalation",
            sources=[],
            tools_used=[PHONE_TRANSFER_TOOL_NAME],
            usage=usage,
        )

    async def _handle_chat_handoff(self, message: str, user_id: str) -> AgentResult:
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
