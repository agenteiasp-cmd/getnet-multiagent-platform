from app.agents.escalation import EscalationAgent
from app.tools.escalation_tool import HandoffConfirmation, PhoneTransferConfirmation


async def test_mock_handoff_call_is_invoked_and_result_captured():
    calls: list[tuple[str, str]] = []

    async def fake_handoff(message: str, user_id: str) -> HandoffConfirmation:
        calls.append((message, user_id))
        return HandoffConfirmation(ticket_id="ESC-TEST01", queue_position=2, estimated_wait_minutes=3)

    agent = EscalationAgent(handoff_call=fake_handoff)

    result = await agent.handle("quero falar com um atendente humano", "user-1")

    assert calls == [("quero falar com um atendente humano", "user-1")]
    assert "ESC-TEST01" in result.response


async def test_escalation_response_confirms_handoff_with_agent_used_escalation():
    async def fake_handoff(message: str, user_id: str) -> HandoffConfirmation:
        return HandoffConfirmation(ticket_id="ESC-ABCDEF12", queue_position=1, estimated_wait_minutes=5)

    agent = EscalationAgent(handoff_call=fake_handoff)

    result = await agent.handle("preciso falar com uma pessoa", "user-1")

    assert result.agent_used == "escalation"
    assert result.intent == "escalation"
    assert "atendente humano" in result.response.lower()


async def test_handoff_call_appears_in_tools_used_and_usage_log():
    async def fake_handoff(message: str, user_id: str) -> HandoffConfirmation:
        return HandoffConfirmation(ticket_id="ESC-ZZZ999", queue_position=1, estimated_wait_minutes=1)

    agent = EscalationAgent(handoff_call=fake_handoff)

    result = await agent.handle("escalar por favor", "user-1")

    assert result.tools_used == ["mock_handoff_call"]
    assert len(result.usage) == 1
    assert result.usage[0].step == "escalation.mock_handoff_call"
    assert result.usage[0].output_data["ticket_id"] == "ESC-ZZZ999"


async def test_phone_call_request_triggers_phone_transfer_instead_of_chat_handoff():
    handoff_calls: list[tuple[str, str]] = []
    phone_calls: list[tuple[str, str]] = []

    async def fake_handoff(message: str, user_id: str) -> HandoffConfirmation:
        handoff_calls.append((message, user_id))
        return HandoffConfirmation(ticket_id="ESC-SHOULDNT", queue_position=1, estimated_wait_minutes=1)

    async def fake_phone_transfer(message: str, user_id: str) -> PhoneTransferConfirmation:
        phone_calls.append((message, user_id))
        return PhoneTransferConfirmation(phone_number="0800 648 8000", access_code="123456")

    agent = EscalationAgent(handoff_call=fake_handoff, phone_transfer_call=fake_phone_transfer)

    result = await agent.handle("quero falar por ligação com um atendente", "user-1")

    assert phone_calls == [("quero falar por ligação com um atendente", "user-1")]
    assert handoff_calls == []
    assert "0800 648 8000" in result.response
    assert "123456" in result.response
    assert result.agent_used == "escalation"
    assert result.intent == "escalation"
    assert result.tools_used == ["mock_phone_transfer_call"]
    assert result.usage[0].step == "escalation.mock_phone_transfer"
    assert result.usage[0].output_data["access_code"] == "123456"


async def test_phone_call_keyword_variants_are_detected():
    async def fake_phone_transfer(message: str, user_id: str) -> PhoneTransferConfirmation:
        return PhoneTransferConfirmation(phone_number="0800 648 8000", access_code="000000")

    agent = EscalationAgent(phone_transfer_call=fake_phone_transfer)

    for message in [
        "quero ligar para vocês",
        "prefiro resolver por telefone",
        "pode me ligar?",
        "vou telefonar para o suporte",
    ]:
        result = await agent.handle(message, "user-1")
        assert result.tools_used == ["mock_phone_transfer_call"], message


async def test_generic_human_request_without_phone_keyword_stays_chat_handoff():
    async def fake_handoff(message: str, user_id: str) -> HandoffConfirmation:
        return HandoffConfirmation(ticket_id="ESC-CHAT01", queue_position=1, estimated_wait_minutes=2)

    agent = EscalationAgent(handoff_call=fake_handoff)

    result = await agent.handle("quero falar com um atendente humano", "user-1")

    assert result.tools_used == ["mock_handoff_call"]
