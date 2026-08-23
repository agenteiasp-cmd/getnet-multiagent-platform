from fastapi import APIRouter, Depends

from app.dependencies import get_orchestrator
from app.models.chat import ChatRequest, ChatResponse
from app.orchestrator import Orchestrator

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, orchestrator: Orchestrator = Depends(get_orchestrator)
) -> ChatResponse:
    outcome = await orchestrator.handle_chat(request.message, request.user_id)
    return ChatResponse(
        response=outcome.result.response,
        agent_used=outcome.result.agent_used,
        intent=outcome.result.intent,
        sources=outcome.result.sources,
        tools_used=outcome.result.tools_used,
        trace_id=outcome.trace_id,
    )
