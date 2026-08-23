from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    user_id: str = Field(min_length=1)


class ChatResponse(BaseModel):
    response: str
    agent_used: str
    intent: str
    sources: list[dict] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    trace_id: str
