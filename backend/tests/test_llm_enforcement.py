from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _fake_ai_message(*, tool_calls=None, finish_reason="stop", content="ok"):
    return SimpleNamespace(
        content=content,
        tool_calls=tool_calls or [],
        usage_metadata={"input_tokens": 10, "output_tokens": 5},
        response_metadata={"finish_reason": finish_reason},
    )


@pytest.mark.parametrize("finish_reason,expected", [("length", True), ("stop", False)])
async def test_router_llm_detects_truncation_on_chitchat_reply(finish_reason, expected):
    from app.llm.router_llm import RouterLLM

    fake_bound = MagicMock()
    fake_bound.ainvoke = AsyncMock(
        return_value=_fake_ai_message(
            tool_calls=[{"name": "classify_intent", "args": {"intent": "chitchat", "reasoning": "x"}, "id": "1"}],
        )
    )
    fake_chitchat = MagicMock()
    fake_chitchat.ainvoke = AsyncMock(return_value=_fake_ai_message(finish_reason=finish_reason))
    fake_classifier_base = MagicMock()
    fake_classifier_base.bind_tools.return_value = fake_bound

    with patch(
        "app.llm.router_llm.ChatOpenAI", side_effect=[fake_classifier_base, fake_chitchat]
    ) as mock_chat_openai:
        llm = RouterLLM(model="gpt-4o-mini", api_key="sk-test", max_tokens=64)
        result = await llm.chitchat_reply("oi")

    classifier_call, chitchat_call = mock_chat_openai.call_args_list
    assert result.truncated is expected


async def test_router_classify_intent_call_is_never_capped():
    """A forced tool call must not have max_tokens applied - a too-low
    ceiling can truncate the tool-call arguments mid-JSON and break
    classification entirely (regression: this crashed with a 500 when a
    user configured a small max_tokens on the Router in the Settings UI)."""
    from app.llm.router_llm import RouterLLM

    fake_bound = MagicMock()
    fake_bound.ainvoke = AsyncMock(
        return_value=_fake_ai_message(
            tool_calls=[{"name": "classify_intent", "args": {"intent": "chitchat", "reasoning": "x"}, "id": "1"}],
        )
    )
    fake_classifier_base = MagicMock()
    fake_classifier_base.bind_tools.return_value = fake_bound
    fake_chitchat = MagicMock()

    with patch(
        "app.llm.router_llm.ChatOpenAI", side_effect=[fake_classifier_base, fake_chitchat]
    ) as mock_chat_openai:
        RouterLLM(model="gpt-4o-mini", api_key="sk-test", max_tokens=10)

    classifier_call, chitchat_call = mock_chat_openai.call_args_list
    assert "max_tokens" not in classifier_call.kwargs
    assert chitchat_call.kwargs["max_tokens"] == 10


async def test_grounded_generator_passes_max_tokens_and_detects_truncation():
    from app.llm.generation import GroundedGenerator

    fake_llm_instance = MagicMock()
    fake_llm_instance.ainvoke = AsyncMock(return_value=_fake_ai_message(finish_reason="length"))

    with patch("app.llm.generation.ChatOpenAI", return_value=fake_llm_instance) as mock_chat_openai:
        generator = GroundedGenerator(model="gpt-4o-mini", api_key="sk-test", max_tokens=32)
        result = await generator.generate("system", "question", "context")

    assert mock_chat_openai.call_args.kwargs["max_tokens"] == 32
    assert result.truncated is True


async def test_support_llm_caps_only_the_final_answer_call():
    """Same reasoning as the Router: the tool-selection call must stay
    uncapped so a low ceiling can't break tool-call parsing."""
    from app.llm.support_llm import SupportLLM

    fake_bound = MagicMock()
    fake_bound.ainvoke = AsyncMock(return_value=_fake_ai_message())
    fake_tool_selector_base = MagicMock()
    fake_tool_selector_base.bind_tools.return_value = fake_bound
    fake_answer_llm = MagicMock()

    with patch(
        "app.llm.support_llm.ChatOpenAI", side_effect=[fake_answer_llm, fake_tool_selector_base]
    ) as mock_chat_openai:
        SupportLLM(model="gpt-4o-mini", api_key="sk-test", max_tokens=10)

    answer_call, tool_selector_call = mock_chat_openai.call_args_list
    assert answer_call.kwargs["max_tokens"] == 10
    assert "max_tokens" not in tool_selector_call.kwargs


def test_support_llm_excludes_disabled_tool_from_bound_tools():
    from app.llm.support_llm import SupportLLM

    fake_llm_instance = MagicMock()
    fake_llm_instance.bind_tools.return_value = MagicMock()

    with patch("app.llm.support_llm.ChatOpenAI", return_value=fake_llm_instance):
        SupportLLM(model="gpt-4o-mini", api_key="sk-test", disabled_features=["get_installment_plan"])

    bound_tool_names = [
        tool["function"]["name"] for tool in fake_llm_instance.bind_tools.call_args[0][0]
    ]
    assert "get_installment_plan" not in bound_tool_names
    assert "get_account_info" in bound_tool_names
