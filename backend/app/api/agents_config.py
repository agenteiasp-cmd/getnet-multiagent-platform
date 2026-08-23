from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config_store.agent_config import AgentConfigStore
from app.dependencies import get_agent_config_store, get_orchestrator

router = APIRouter()


class AgentConfigUpdate(BaseModel):
    prompt: str | None = None
    model: str | None = None
    temperature: float | None = None
    tools: list[str] | None = None
    enabled: bool | None = None
    max_tokens: int | None = None
    disabled_features: list[str] | None = None


@router.get("/agents/config")
def get_all_agent_configs(store: AgentConfigStore = Depends(get_agent_config_store)) -> dict:
    return store.get_all()


@router.put("/agents/config/{agent}")
def update_agent_config(
    agent: str,
    update: AgentConfigUpdate,
    store: AgentConfigStore = Depends(get_agent_config_store),
) -> dict:
    updates = {k: v for k, v in update.model_dump().items() if v is not None}
    try:
        result = store.update(agent, updates)
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")
    get_orchestrator.cache_clear()
    return result


@router.post("/agents/config/{agent}/restore-default")
def restore_agent_config_default(
    agent: str, store: AgentConfigStore = Depends(get_agent_config_store)
) -> dict:
    try:
        result = store.restore_default(agent)
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")
    get_orchestrator.cache_clear()
    return result
