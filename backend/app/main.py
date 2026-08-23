from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agents_config import router as agents_config_router
from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router
from app.api.feedback import router as feedback_router
from app.api.metrics import router as metrics_router
from app.api.test_runner import router as test_runner_router

app = FastAPI(
    title="Getnet Multiagent Support API",
    description="Orchestration backend for the Getnet multiagent customer support platform.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(metrics_router)
app.include_router(agents_config_router)
app.include_router(test_runner_router)
app.include_router(feedback_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
