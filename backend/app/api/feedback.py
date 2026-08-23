from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies import get_observability_store
from app.observability.store import ObservabilityStore

router = APIRouter()


class FeedbackRequest(BaseModel):
    trace_id: str = Field(min_length=1)
    agent_used: str = Field(min_length=1)
    rating: int = Field(description="1 for positive (👍), -1 for negative (👎)")


@router.post("/feedback")
def submit_feedback(
    request: FeedbackRequest, store: ObservabilityStore = Depends(get_observability_store)
) -> dict:
    created_at = datetime.now(timezone.utc).isoformat()
    store.insert_feedback(
        trace_id=request.trace_id,
        agent_used=request.agent_used,
        rating=request.rating,
        created_at=created_at,
    )
    return {"status": "ok"}


@router.get("/agents/feedback")
def get_agents_feedback(
    start: str | None = None,
    end: str | None = None,
    store: ObservabilityStore = Depends(get_observability_store),
) -> dict:
    return store.agent_feedback(start=start, end=end)
