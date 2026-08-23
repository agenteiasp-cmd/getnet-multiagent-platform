from typing import Literal

Intent = Literal["knowledge", "support", "escalation", "chitchat"]

INTENTS: tuple[Intent, ...] = ("knowledge", "support", "escalation", "chitchat")

CLASSIFY_INTENT_TOOL = {
    "type": "function",
    "function": {
        "name": "classify_intent",
        "description": (
            "Classify the user's message into exactly one support intent: "
            "'knowledge' for ANY informational question - about Getnet products/policies, "
            "or about anything else in the world (weather, general trivia, etc.) - "
            "anything that asks for information rather than the user's own account data, "
            "'support' for questions about the user's OWN account/transactions/device/plan "
            "(phrasing like 'my', 'minha', 'meu' pointing at their specific situation), "
            "'escalation' for requests to speak with a human agent, "
            "'chitchat' ONLY for greetings, thanks, and casual pleasantries with no "
            "information request and no account request at all."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": list(INTENTS),
                    "description": "The single best-fit intent category.",
                },
                "reasoning": {
                    "type": "string",
                    "description": "One short sentence explaining the classification.",
                },
            },
            "required": ["intent", "reasoning"],
        },
    },
}

CLASSIFY_INTENT_TOOL_CHOICE = {
    "type": "function",
    "function": {"name": "classify_intent"},
}
