from datetime import datetime, timezone

from app.models.pipeline import UsageRecord
from app.observability.jsonl_logger import JsonlLogger
from app.observability.models import StepRecord
from app.observability.store import ObservabilityStore


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ObservabilityRecorder:
    """Writes one conversation row plus one step row per UsageRecord, to
    both the JSONL append log and its SQLite index, for every /chat call.
    Each /chat call is treated as one conversation (conversation_id ==
    trace_id) - the API has no multi-turn session concept."""

    def __init__(self, jsonl_logger: JsonlLogger, store: ObservabilityStore):
        self._jsonl = jsonl_logger
        self._store = store

    def record_chat(
        self,
        *,
        trace_id: str,
        user_id: str,
        message: str,
        response: str,
        agent_used: str,
        intent: str,
        status: str,
        usage: list[UsageRecord],
    ) -> None:
        conversation_id = trace_id
        timestamp = now_iso()

        self._store.upsert_conversation(
            conversation_id=conversation_id,
            trace_id=trace_id,
            user_id=user_id,
            message=message,
            response=response,
            agent_used=agent_used,
            intent=intent,
            status=status,
            created_at=timestamp,
        )

        for entry in usage:
            record = StepRecord(
                trace_id=trace_id,
                conversation_id=conversation_id,
                step=entry.step,
                timestamp=timestamp,
                input=entry.input_data,
                output=entry.output_data,
                model=entry.model,
                prompt_tokens=entry.prompt_tokens,
                completion_tokens=entry.completion_tokens,
                latency_ms=entry.latency_ms,
                status=entry.status,
            )
            self._jsonl.append(record)
            self._store.insert_step(record)
