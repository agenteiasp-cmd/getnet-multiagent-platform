from dataclasses import dataclass
from typing import Any


@dataclass
class StepRecord:
    trace_id: str
    conversation_id: str
    step: str
    timestamp: str
    input: Any
    output: Any
    model: str | None
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    status: str
