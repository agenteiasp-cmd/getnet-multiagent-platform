from typing import Protocol

from app.data.mock_users import get_user
from app.models.pipeline import AgentResult, UsageRecord
from app.tools.support_tools import execute_support_tool

UNKNOWN_USER_MESSAGE = (
    "Não encontrei uma conta associada a este usuário. Verifique se você "
    "está logado com a conta correta ou fale com um atendente humano para "
    "regularizar seu cadastro."
)


class SupportLLMProtocol(Protocol):
    async def decide_tools(self, message: str): ...
    async def generate_answer(self, message: str, ai_message, tool_outputs: list[tuple[str, str, dict]]): ...


class SupportAgent:
    """Answers account-specific questions by letting the LLM pick which
    support tool(s) to call, executing them against the requesting user's
    mocked data only, then generating the final answer from the results."""

    def __init__(self, support_llm: SupportLLMProtocol):
        self._llm = support_llm

    async def handle(self, message: str, user_id: str) -> AgentResult:
        user_data = get_user(user_id)
        if user_data is None:
            return AgentResult(
                response=UNKNOWN_USER_MESSAGE,
                agent_used="support",
                intent="support",
                sources=[],
                tools_used=[],
                usage=[],
            )

        decision, ai_message = await self._llm.decide_tools(message)
        decide_usage = UsageRecord(
            step="support.decide_tools",
            model=decision.model,
            input_data=message,
            output_data=[tc.name for tc in decision.tool_calls],
            prompt_tokens=decision.prompt_tokens,
            completion_tokens=decision.completion_tokens,
            latency_ms=decision.latency_ms,
            status="truncated" if decision.truncated else "ok",
        )

        tool_outputs: list[tuple[str, str, dict]] = []
        tools_used: list[str] = []
        for tool_call in decision.tool_calls:
            result = execute_support_tool(tool_call.name, user_data)
            tool_outputs.append((tool_call.id, tool_call.name, result))
            tools_used.append(tool_call.name)

        generation = await self._llm.generate_answer(message, ai_message, tool_outputs)
        generate_usage = UsageRecord(
            step="support.generate_answer",
            model=generation.model,
            input_data=tool_outputs,
            output_data=generation.text,
            prompt_tokens=generation.prompt_tokens,
            completion_tokens=generation.completion_tokens,
            latency_ms=generation.latency_ms,
            status="truncated" if generation.truncated else "ok",
        )

        return AgentResult(
            response=generation.text,
            agent_used="support",
            intent="support",
            sources=[],
            tools_used=tools_used,
            usage=[decide_usage, generate_usage],
        )
