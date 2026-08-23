from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_observability_store
from app.observability.store import ObservabilityStore

router = APIRouter()


@router.get("/conversations")
def list_conversations(
    start: str | None = None,
    end: str | None = None,
    agent: str | None = None,
    status: str | None = None,
    limit: int = Query(default=100, le=500),
    store: ObservabilityStore = Depends(get_observability_store),
) -> list[dict]:
    return store.list_conversations(start=start, end=end, agent=agent, status=status, limit=limit)


@router.get("/conversations/{conversation_id}/trace")
def get_conversation_trace(
    conversation_id: str, store: ObservabilityStore = Depends(get_observability_store)
) -> dict:
    conversation = store.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    steps = store.get_steps(conversation_id)
    return {"conversation": conversation, "steps": steps}
