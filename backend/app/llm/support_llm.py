import time
from dataclasses import dataclass, field

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.tools.support_tools import SUPPORT_TOOL_SCHEMAS

SUPPORT_SYSTEM_PROMPT = (
    "Você é o agente de suporte da Getnet. Use as tools disponíveis para "
    "consultar os dados do lojista (conta/Pix, prazo de depósito, "
    "transações, status da maquininha, plano de parcelamento) antes de "
    "responder. Chame apenas as tools relevantes para a pergunta. Depois "
    "de obter os resultados, responda de forma clara e objetiva usando "
    "somente esses dados."
)


def _is_truncated(message) -> bool:
    metadata = getattr(message, "response_metadata", None) or {}
    return metadata.get("finish_reason") == "length"


@dataclass
class ToolCall:
    name: str
    id: str


@dataclass
class ToolDecision:
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    truncated: bool = False


@dataclass
class GenerationResult:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    truncated: bool = False


class SupportLLM:
    """Two-round-trip tool-calling flow: the model first decides which
    support tools (if any) are relevant, then - once given their results -
    produces the final answer."""

    def __init__(
        self,
        model: str,
        api_key: str,
        max_tokens: int | None = None,
        disabled_features: list[str] | None = None,
    ):
        self.model = model
        self._api_key = api_key
        # max_tokens applies only to the final answer (an open-ended
        # generation): the tool-selection call is kept uncapped so a low
        # ceiling can't truncate tool-call arguments mid-JSON - same
        # reasoning as RouterLLM's classify() call.
        self._llm = ChatOpenAI(model=model, api_key=api_key, temperature=0, max_tokens=max_tokens)
        self._tool_selector = ChatOpenAI(model=model, api_key=api_key, temperature=0)
        disabled = set(disabled_features or [])
        available_tools = [
            schema
            for schema in SUPPORT_TOOL_SCHEMAS
            if schema["function"]["name"] not in disabled
        ]
        self._llm_with_tools = self._tool_selector.bind_tools(available_tools)

    async def decide_tools(self, message: str) -> tuple[ToolDecision, AIMessage]:
        start = time.perf_counter()
        ai_message = await self._llm_with_tools.ainvoke(
            [SystemMessage(content=SUPPORT_SYSTEM_PROMPT), HumanMessage(content=message)]
        )
        latency_ms = (time.perf_counter() - start) * 1000
        usage = getattr(ai_message, "usage_metadata", None) or {}
        decision = ToolDecision(
            tool_calls=[ToolCall(name=tc["name"], id=tc["id"]) for tc in ai_message.tool_calls],
            model=self.model,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            latency_ms=latency_ms,
            truncated=_is_truncated(ai_message),
        )
        return decision, ai_message

    async def generate_answer(
        self, message: str, ai_message: AIMessage, tool_outputs: list[tuple[str, str, dict]]
    ) -> GenerationResult:
        """tool_outputs: list of (tool_call_id, tool_name, result_dict)."""
        messages = [
            SystemMessage(content=SUPPORT_SYSTEM_PROMPT),
            HumanMessage(content=message),
            ai_message,
        ]
        for tool_call_id, _tool_name, result in tool_outputs:
            messages.append(ToolMessage(content=str(result), tool_call_id=tool_call_id))

        start = time.perf_counter()
        final_message = await self._llm.ainvoke(messages)
        latency_ms = (time.perf_counter() - start) * 1000
        usage = getattr(final_message, "usage_metadata", None) or {}
        return GenerationResult(
            text=final_message.content,
            model=self.model,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            latency_ms=latency_ms,
            truncated=_is_truncated(final_message),
        )
