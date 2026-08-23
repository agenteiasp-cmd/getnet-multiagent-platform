from dataclasses import dataclass, field

import pytest

from app.agents.support import SupportAgent, UNKNOWN_USER_MESSAGE
from app.data.mock_users import MOCK_USERS, get_user


@dataclass
class FakeToolCall:
    name: str
    id: str = "call-1"


@dataclass
class FakeDecision:
    tool_calls: list[FakeToolCall] = field(default_factory=list)
    model: str = "gpt-4o-mini"
    prompt_tokens: int = 10
    completion_tokens: int = 5
    latency_ms: float = 5.0
    truncated: bool = False


@dataclass
class FakeGeneration:
    text: str
    model: str = "gpt-4o-mini"
    prompt_tokens: int = 12
    completion_tokens: int = 8
    latency_ms: float = 7.0
    truncated: bool = False


class FakeSupportLLM:
    def __init__(self, tool_names: list[str], answer: str):
        self._decision = FakeDecision(tool_calls=[FakeToolCall(name=n) for n in tool_names])
        self._answer = answer
        self.generate_calls: list[list[tuple]] = []

    async def decide_tools(self, message: str):
        return self._decision, object()

    async def generate_answer(self, message: str, ai_message, tool_outputs):
        self.generate_calls.append(tool_outputs)
        return FakeGeneration(text=self._answer)


def test_fixtures_cover_every_example_case():
    for user_id in ("user-1", "user-2"):
        data = MOCK_USERS[user_id]
        assert "account" in data and data["account"]["pix_key"]
        assert "settlement" in data
        assert "device" in data
        assert any(t["status"] == "declined" for t in MOCK_USERS["user-1"]["transactions"])
        assert "installments" in data


async def test_deposit_timing_question_invokes_settlement_tool():
    llm = FakeSupportLLM(["get_settlement_schedule"], "Seu próximo depósito é em 1 dia útil.")
    agent = SupportAgent(llm)

    result = await agent.handle("quando cai o dinheiro das minhas vendas?", "user-1")

    assert result.tools_used == ["get_settlement_schedule"]
    assert result.agent_used == "support"


async def test_transaction_status_question_invokes_transaction_tool():
    llm = FakeSupportLLM(["get_transaction_status"], "Sua transação foi recusada por saldo insuficiente.")
    agent = SupportAgent(llm)

    result = await agent.handle("por que minha transação foi recusada?", "user-1")

    assert result.tools_used == ["get_transaction_status"]
    assert "recusada" in result.response.lower()


async def test_pix_bank_account_question():
    llm = FakeSupportLLM(["get_account_info"], "Sua chave Pix cadastrada é maria.souza@example.com.")
    agent = SupportAgent(llm)

    result = await agent.handle("qual conta está cadastrada para receber Pix?", "user-1")

    assert result.tools_used == ["get_account_info"]
    assert "pix" in result.response.lower()


async def test_maquininha_sem_internet_question():
    llm = FakeSupportLLM(["get_device_status"], "Sua maquininha está offline há 2 horas.")
    agent = SupportAgent(llm)

    result = await agent.handle("minha maquininha está sem internet", "user-1")

    assert result.tools_used == ["get_device_status"]


async def test_crediario_installments_question():
    llm = FakeSupportLLM(["get_installment_plan"], "Seu plano é 6x de R$ 150,00 sem juros.")
    agent = SupportAgent(llm)

    result = await agent.handle("como funciona o parcelamento no crediário?", "user-1")

    assert result.tools_used == ["get_installment_plan"]


async def test_tool_results_are_scoped_to_requesting_user():
    llm = FakeSupportLLM(["get_account_info"], "resposta")
    agent = SupportAgent(llm)

    result = await agent.handle("qual minha conta?", "user-2")

    tool_outputs = llm.generate_calls[0]
    _, _, result_payload = tool_outputs[0]
    assert result_payload == MOCK_USERS["user-2"]["account"]
    assert result_payload != MOCK_USERS["user-1"]["account"]


async def test_unknown_user_id_returns_graceful_fallback():
    llm = FakeSupportLLM([], "não deveria ser chamado")
    agent = SupportAgent(llm)

    result = await agent.handle("qualquer pergunta", "user-does-not-exist")

    assert result.response == UNKNOWN_USER_MESSAGE
    assert result.tools_used == []
    assert get_user("user-does-not-exist") is None
