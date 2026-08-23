from dataclasses import dataclass

import pytest

from app.agents.router import RouterAgent


@dataclass
class FakeClassification:
    intent: str
    reasoning: str
    model: str = "gpt-4o-mini"
    prompt_tokens: int = 10
    completion_tokens: int = 5
    latency_ms: float = 12.0
    truncated: bool = False


@dataclass
class FakeChitchatReply:
    text: str
    model: str = "gpt-4o-mini"
    prompt_tokens: int = 8
    completion_tokens: int = 6
    latency_ms: float = 9.0
    truncated: bool = False


class FakeRouterLLM:
    """Stand-in for RouterLLM: unit tests never touch the real LLM, only
    the RouterAgent's forced-tool-call contract with whatever the LLM
    layer returns."""

    def __init__(self, classification: FakeClassification, chitchat_text: str = "Oi! Como posso ajudar?"):
        self._classification = classification
        self._chitchat_text = chitchat_text
        self.classify_calls: list[str] = []
        self.chitchat_calls: list[str] = []

    async def classify(self, message: str):
        self.classify_calls.append(message)
        return self._classification

    async def chitchat_reply(self, message: str):
        self.chitchat_calls.append(message)
        return FakeChitchatReply(text=self._chitchat_text)


@pytest.mark.parametrize(
    "intent",
    ["knowledge", "support", "escalation"],
)
async def test_router_dispatches_non_chitchat_intents_without_answering(intent):
    fake_llm = FakeRouterLLM(FakeClassification(intent=intent, reasoning="test"))
    router = RouterAgent(fake_llm)

    outcome = await router.route("mensagem qualquer")

    assert outcome.intent == intent
    assert outcome.result is None
    assert fake_llm.chitchat_calls == []
    assert len(outcome.usage) == 1
    assert outcome.usage[0].step == "router.classify_intent"


async def test_router_always_uses_tool_call_result():
    fake_llm = FakeRouterLLM(FakeClassification(intent="support", reasoning="conta do usuário"))
    router = RouterAgent(fake_llm)

    outcome = await router.route("quero saber sobre minha conta")

    assert fake_llm.classify_calls == ["quero saber sobre minha conta"]
    assert outcome.intent == "support"


async def test_router_answers_chitchat_directly_without_dispatch():
    fake_llm = FakeRouterLLM(
        FakeClassification(intent="chitchat", reasoning="saudação"),
        chitchat_text="Olá! Tudo bem?",
    )
    router = RouterAgent(fake_llm)

    outcome = await router.route("oi, tudo bem?")

    assert outcome.intent == "chitchat"
    assert outcome.result is not None
    assert outcome.result.agent_used == "router"
    assert outcome.result.response == "Olá! Tudo bem?"
    assert outcome.result.tools_used == ["classify_intent"]
    assert outcome.result.sources == []
    assert fake_llm.chitchat_calls == ["oi, tudo bem?"]
