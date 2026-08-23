from dataclasses import dataclass, field


@dataclass
class UsageRecord:
    """One LLM/tool call's observability footprint, used later by the
    observability logger (section 9) to build per-step trace records."""

    step: str
    model: str | None = None
    input_data: object = None
    output_data: object = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    status: str = "ok"


@dataclass
class AgentResult:
    response: str
    agent_used: str
    intent: str
    sources: list[dict] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    usage: list[UsageRecord] = field(default_factory=list)
