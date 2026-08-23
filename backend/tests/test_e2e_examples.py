"""End-to-end test against the challenge's 10 example cases, run against
the real orchestrator (real OpenAI/Pinecone/Tavily calls). Skipped
automatically when credentials aren't configured - see conftest.py.
"""

import pytest

from app.dependencies import get_orchestrator
from tests.conftest import requires_live_credentials

EXAMPLE_CASES = [
    ("Qual a diferença entre a Get Clássica e a Get Smart?", "user-1", "knowledge"),
    ("Qual a previsão do tempo para amanhã em São Paulo?", "user-1", "knowledge"),
    ("Quando cai o dinheiro das minhas vendas?", "user-1", "support"),
    ("Qual conta bancária está cadastrada para receber via Pix?", "user-1", "support"),
    ("Minha maquininha está sem internet, o que eu faço?", "user-1", "support"),
    ("Como funciona a antecipação de recebíveis da Getnet?", "user-1", "knowledge"),
    ("Minha transação foi recusada, por que isso aconteceu?", "user-1", "support"),
    ("Qual é o meu plano de parcelamento no crediário da minha loja?", "user-1", "support"),
    ("Como eu vendo pelo WhatsApp usando o Payment Link da Getnet?", "user-1", "knowledge"),
    ("Quero falar com um atendente humano, pode me transferir?", "user-1", "escalation"),
]


@requires_live_credentials
@pytest.mark.parametrize("message,user_id,expected_intent", EXAMPLE_CASES)
async def test_challenge_example_case_returns_well_formed_response(message, user_id, expected_intent):
    get_orchestrator.cache_clear()
    orchestrator = get_orchestrator()

    outcome = await orchestrator.handle_chat(message, user_id)

    assert outcome.trace_id
    assert outcome.result.response.strip()
    assert outcome.result.intent == expected_intent
    assert outcome.result.agent_used
