from fastapi import APIRouter, Depends

from app.dependencies import get_observability_store
from app.observability.store import ObservabilityStore

router = APIRouter()


@router.get("/metrics")
def get_metrics(
    start: str | None = None,
    end: str | None = None,
    store: ObservabilityStore = Depends(get_observability_store),
) -> dict:
    return store.metrics_summary(start=start, end=end)


@router.get("/agents/usage")
def get_agents_usage(
    start: str | None = None,
    end: str | None = None,
    store: ObservabilityStore = Depends(get_observability_store),
) -> dict:
    return store.agent_usage(start=start, end=end)


@router.get("/tokens/usage")
def get_tokens_usage(
    start: str | None = None,
    end: str | None = None,
    store: ObservabilityStore = Depends(get_observability_store),
) -> dict:
    return store.token_usage(start=start, end=end)
