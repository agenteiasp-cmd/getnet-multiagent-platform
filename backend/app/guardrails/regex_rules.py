import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailRule:
    name: str
    pattern: re.Pattern
    reason: str


# Curated, challenge-scope regex rules. Not a hardened content-safety
# system - see design.md "Non-Goals". Each rule targets a concrete,
# testable pattern rather than broad heuristics.
RULES: list[GuardrailRule] = [
    GuardrailRule(
        name="prompt_injection_ignore_instructions",
        pattern=re.compile(
            r"\b(ignore|desconsidere|esque[çc]a)\b.{0,40}\b(instru[çc][õo]es|prompt|regras)\b",
            re.IGNORECASE,
        ),
        reason="Attempted prompt injection: instructs the system to ignore its instructions.",
    ),
    GuardrailRule(
        name="prompt_injection_reveal_system_prompt",
        pattern=re.compile(
            r"\b(reveal|mostre|exiba|repita|print)\b.{0,40}\b(system prompt|prompt do sistema|suas instru[çc][õo]es)\b",
            re.IGNORECASE,
        ),
        reason="Attempted prompt injection: requests disclosure of the system prompt.",
    ),
    GuardrailRule(
        name="secret_exfiltration_api_key",
        pattern=re.compile(
            r"\b(api[_ ]?key|chave de api|access[_ ]?token|senha do banco|database password)\b",
            re.IGNORECASE,
        ),
        reason="Attempted secret exfiltration: asks for credentials/API keys.",
    ),
    GuardrailRule(
        name="credit_card_number",
        pattern=re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
        reason="Message contains what looks like a full card/account number.",
    ),
    GuardrailRule(
        name="jailbreak_circumvention",
        pattern=re.compile(
            r"\b(burlar|contornar|bypass|jailbreak)\b"
            r"|\bmodo (dev|desenvolvedor|sem restri[çc][õo]es|irrestrito)\b"
            r"|\bfinja que (voc[êe]|voce) (n[ãa]o tem|pode ignorar)\b",
            re.IGNORECASE,
        ),
        reason="Attempted jailbreak: asks the assistant to circumvent its own rules.",
    ),
    GuardrailRule(
        name="cross_customer_data_request",
        pattern=re.compile(
            r"\b(dados|informa[çc][õo]es|saldo|extrato|senha|cadastro)\b.{0,40}"
            r"\b(de outro|de outra|do outro|da outra)\b.{0,20}"
            r"\b(cliente|usu[áa]rio|conta|pessoa|cpf|cnpj)\b",
            re.IGNORECASE,
        ),
        reason="Attempted access to another customer's data - cross-tenant risk.",
    ),
    GuardrailRule(
        name="platform_integrity_risk",
        pattern=re.compile(
            r"\b(apag\w*|delet\w*|exclu\w*|derrub\w*|desativ\w*|drop\w*)\b.{0,40}"
            r"\b(banco de dados|database|servidor|plataforma|sistema|tabela)\b",
            re.IGNORECASE,
        ),
        reason="Attempted action that could compromise platform integrity.",
    ),
]


def check_regex(message: str) -> GuardrailRule | None:
    """Return the first matching rule, or None if the message is clean."""
    for rule in RULES:
        if rule.pattern.search(message):
            return rule
    return None
