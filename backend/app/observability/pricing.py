# USD per 1M tokens. Approximate public OpenAI pricing at implementation
# time - used only to estimate cost for the dashboard, not for billing.
MODEL_PRICING_PER_MILLION_TOKENS: dict[str, dict[str, float]] = {
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
}

DEFAULT_PRICING = {"prompt": 0.15, "completion": 0.60}


def estimate_cost_usd(model: str | None, prompt_tokens: int, completion_tokens: int) -> float:
    pricing = MODEL_PRICING_PER_MILLION_TOKENS.get(model or "", DEFAULT_PRICING)
    return (
        prompt_tokens * pricing["prompt"] / 1_000_000
        + completion_tokens * pricing["completion"] / 1_000_000
    )
