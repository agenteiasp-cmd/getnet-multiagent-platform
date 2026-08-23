from app.agents.escalation import EscalationAgent
from app.tools.escalation_tool import HandoffConfirmation


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
