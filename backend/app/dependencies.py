from functools import lru_cache
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from tavily import AsyncTavilyClient

from app.agents.escalation import EscalationAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.router import RouterAgent
from app.agents.support import SupportAgent
from app.config import get_settings
from app.config_store.agent_config import AgentConfigStore
from app.llm.client import get_openai_client
from app.llm.generation import GroundedGenerator
from app.llm.router_llm import RouterLLM
from app.llm.support_llm import SupportLLM
from app.observability.jsonl_logger import JsonlLogger
from app.observability.recorder import ObservabilityRecorder
from app.observability.store import ObservabilityStore
from app.orchestrator import Orchestrator
from app.tools.retrieval import PineconeRetrievalTool
from app.tools.web_search import TavilyWebSearchTool

EMBEDDING_MODEL = "text-embedding-3-small"


@lru_cache
def get_vector_store() -> PineconeVectorStore:
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=settings.openai_api_key)
    return PineconeVectorStore(index=index, embedding=embeddings)


@lru_cache
def get_observability_store() -> ObservabilityStore:
    settings = get_settings()
    return ObservabilityStore(Path(settings.data_dir) / "observability.db")


@lru_cache
def get_jsonl_logger() -> JsonlLogger:
    settings = get_settings()
    return JsonlLogger(Path(settings.data_dir) / "events.jsonl")


@lru_cache
def get_observability_recorder() -> ObservabilityRecorder:
    return ObservabilityRecorder(get_jsonl_logger(), get_observability_store())


@lru_cache
def get_agent_config_store() -> AgentConfigStore:
    settings = get_settings()
    return AgentConfigStore(Path(settings.data_dir) / "agent_config.json")


@lru_cache
def get_orchestrator() -> Orchestrator:
    """Cached, but the cache is cleared by the agents_config API whenever
    `max_tokens`/`disabled_features` change (see app/api/agents_config.py),
    so enforcement of those two fields takes effect on the next request
    without needing a process restart."""
    settings = get_settings()
    client = get_openai_client()
    agent_configs = get_agent_config_store().get_all()

    def _max_tokens(agent: str) -> int | None:
        return agent_configs.get(agent, {}).get("max_tokens")

    def _disabled_features(agent: str) -> list[str]:
        return agent_configs.get(agent, {}).get("disabled_features") or []

    router = RouterAgent(
        RouterLLM(
            model=settings.router_model,
            api_key=settings.openai_api_key,
            max_tokens=_max_tokens("router"),
        )
    )

    retrieval_tool = PineconeRetrievalTool(get_vector_store())
    tavily_client = AsyncTavilyClient(api_key=settings.tavily_api_key)
    web_search_tool = TavilyWebSearchTool(tavily_client)
    generator = GroundedGenerator(
        model=settings.knowledge_model,
        api_key=settings.openai_api_key,
        max_tokens=_max_tokens("knowledge"),
    )
    knowledge_agent = KnowledgeAgent(
        retrieval_tool,
        web_search_tool,
        generator,
        disabled_features=_disabled_features("knowledge"),
    )

    support_agent = SupportAgent(
        SupportLLM(
            model=settings.support_model,
            api_key=settings.openai_api_key,
            max_tokens=_max_tokens("support"),
            disabled_features=_disabled_features("support"),
        )
    )

    escalation_agent = EscalationAgent()

    return Orchestrator(
        openai_client=client,
        router=router,
        knowledge_agent=knowledge_agent,
        support_agent=support_agent,
        escalation_agent=escalation_agent,
        recorder=get_observability_recorder(),
    )
