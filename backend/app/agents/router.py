from dataclasses import dataclass
from typing import Protocol

from app.models.pipeline import AgentResult, UsageRecord
from app.tools.classify_intent import Intent


class RouterLLMProtocol(Protocol):
    async def classify(self, message: str): ...
    async def chitchat_reply(self, message: str): ...


@dataclass
class RouterOutcome:
    intent: Intent
    reasoning: str
    result: AgentResult | None
    usage: list[UsageRecord]


class RouterAgent:
    """Classifies intent via a forced classify_intent tool call and
    answers chitchat directly. Never infers intent from free text.
    """

    def __init__(self, router_llm: RouterLLMProtocol):
        self._llm = router_llm

    async def route(self, message: str) -> RouterOutcome:
        classification = await self._llm.classify(message)
        classify_usage = UsageRecord(
            step="router.classify_intent",
            model=classification.model,
            input_data=message,
            output_data={"intent": classification.intent, "reasoning": classification.reasoning},
            prompt_tokens=classification.prompt_tokens,
            completion_tokens=classification.completion_tokens,
            latency_ms=classification.latency_ms,
            status="truncated" if classification.truncated else "ok",
        )

        if classification.intent != "chitchat":
            return RouterOutcome(
                intent=classification.intent,
                reasoning=classification.reasoning,
                result=None,
                usage=[classify_usage],
            )

        reply = await self._llm.chitchat_reply(message)
        reply_usage = UsageRecord(
            step="router.chitchat_reply",
            model=reply.model,
            input_data=message,
            output_data=reply.text,
            prompt_tokens=reply.prompt_tokens,
            completion_tokens=reply.completion_tokens,
            latency_ms=reply.latency_ms,
            status="truncated" if reply.truncated else "ok",
        )
        result = AgentResult(
            response=reply.text,
            agent_used="router",
            intent="chitchat",
            sources=[],
            tools_used=["classify_intent"],
            usage=[classify_usage, reply_usage],
        )
        return RouterOutcome(
            intent="chitchat",
            reasoning=classification.reasoning,
            result=result,
            usage=[classify_usage, reply_usage],
        )
