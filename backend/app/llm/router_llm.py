import time
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.tools.classify_intent import CLASSIFY_INTENT_TOOL, Intent

ROUTER_SYSTEM_PROMPT = (
    "Você é o roteador de um sistema de atendimento da Getnet. Sua única "
    "tarefa ao classificar é chamar a tool classify_intent com o intent mais "
    "adequado para a mensagem do usuário.\n\n"
    "Regras importantes:\n"
    "- 'knowledge' é para QUALQUER pergunta que peça uma informação: sobre "
    "produtos/políticas da Getnet OU sobre qualquer outro assunto do mundo "
    "(ex: previsão do tempo, curiosidades). Se a pergunta busca uma "
    "informação e não é sobre a conta específica do usuário, é 'knowledge'.\n"
    "- 'support' é SOMENTE para perguntas sobre a própria conta/transação/"
    "maquininha/plano do usuário (ex: 'minha conta', 'meu parcelamento', "
    "'minha transação').\n"
    "- 'chitchat' é SOMENTE para saudações, agradecimentos e conversa "
    "social sem nenhum pedido de informação ou de conta.\n"
    "- 'escalation' é para pedidos explícitos de falar com um humano."
)

CHITCHAT_SYSTEM_PROMPT = (
    "Você é o assistente virtual da Getnet. Responda de forma breve, "
    "amigável e profissional a mensagens de conversa casual (saudações, "
    "agradecimentos, etc.) que não pedem informação sobre produtos, conta "
    "ou escalonamento."
)


def _is_truncated(ai_message) -> bool:
    """True when the call stopped because it hit the model's max-output-
    tokens cap, per the response's finish_reason (OpenAI convention)."""
    metadata = getattr(ai_message, "response_metadata", None) or {}
    return metadata.get("finish_reason") == "length"


@dataclass
class ClassificationResult:
    intent: Intent
    reasoning: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    truncated: bool = False


@dataclass
class ChitchatReply:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    truncated: bool = False


class RouterLLM:
    """Wraps a LangChain ChatOpenAI model: one call path with the
    classify_intent tool forced via tool_choice, one plain call path for
    direct chitchat replies.
    """

    def __init__(self, model: str, api_key: str, max_tokens: int | None = None):
        self.model = model
        # The configured max_tokens ceiling is NOT applied to the forced
        # classify_intent tool call: its output is already small/structured,
        # and a too-low ceiling can truncate the tool-call arguments before
        # they're valid JSON, breaking classification entirely instead of
        # just returning a shorter answer. The ceiling is only meaningful
        # for open-ended generation, so it applies to the chitchat reply.
        self._classifier = ChatOpenAI(model=model, api_key=api_key, temperature=0).bind_tools(
            [CLASSIFY_INTENT_TOOL], tool_choice="classify_intent"
        )
        self._chitchat = ChatOpenAI(
            model=model, api_key=api_key, temperature=0.7, max_tokens=max_tokens
        )

    async def classify(self, message: str) -> ClassificationResult:
        start = time.perf_counter()
        ai_message = await self._classifier.ainvoke(
            [SystemMessage(content=ROUTER_SYSTEM_PROMPT), HumanMessage(content=message)]
        )
        latency_ms = (time.perf_counter() - start) * 1000

        if not ai_message.tool_calls:
            raise RuntimeError(
                "Router LLM did not return the forced classify_intent tool call."
            )
        args = ai_message.tool_calls[0]["args"]
        usage = getattr(ai_message, "usage_metadata", None) or {}
        return ClassificationResult(
            intent=args["intent"],
            reasoning=args.get("reasoning", ""),
            model=self.model,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            latency_ms=latency_ms,
            truncated=_is_truncated(ai_message),
        )

    async def chitchat_reply(self, message: str) -> ChitchatReply:
        start = time.perf_counter()
        ai_message = await self._chitchat.ainvoke(
            [SystemMessage(content=CHITCHAT_SYSTEM_PROMPT), HumanMessage(content=message)]
        )
        latency_ms = (time.perf_counter() - start) * 1000
        usage = getattr(ai_message, "usage_metadata", None) or {}
        return ChitchatReply(
            text=ai_message.content,
            model=self.model,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            latency_ms=latency_ms,
            truncated=_is_truncated(ai_message),
        )
