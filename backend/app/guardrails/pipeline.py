from dataclasses import dataclass

from openai import AsyncOpenAI

from app.guardrails.moderation import check_moderation
from app.guardrails.regex_rules import check_regex


@dataclass(frozen=True)
class GuardrailResult:
    blocked: bool
    reason: str | None = None
    rule_name: str | None = None


REFUSAL_MESSAGE = (
    "Não posso ajudar com essa solicitação. Se precisar de suporte sobre sua "
    "conta, produtos Getnet ou quiser falar com um atendente humano, me diga "
    "como posso ajudar."
)


async def run_guardrails(message: str, client: AsyncOpenAI) -> GuardrailResult:
    """Run regex checks then moderation. Regex is cheap and runs first so a
    moderation API call is skipped entirely when a message is already
    rejected by a local rule.
    """
    regex_match = check_regex(message)
    if regex_match is not None:
        return GuardrailResult(
            blocked=True, reason=regex_match.reason, rule_name=regex_match.name
        )

    moderation = await check_moderation(message, client)
    if moderation.flagged:
        return GuardrailResult(
            blocked=True,
            reason=f"Flagged by moderation: {', '.join(moderation.categories)}",
            rule_name="moderation",
        )

    return GuardrailResult(blocked=False)
