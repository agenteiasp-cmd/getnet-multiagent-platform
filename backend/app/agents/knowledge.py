from typing import Protocol

from app.models.pipeline import AgentResult, UsageRecord
from app.tools.retrieval import PineconeRetrievalTool
from app.tools.web_search import TavilyWebSearchTool

RAG_SYSTEM_PROMPT = (
    "Você é o assistente de conhecimento da Getnet. Responda à pergunta do "
    "usuário usando exclusivamente o contexto fornecido, extraído do site "
    "oficial da Getnet. Seja claro e direto. Se o contexto não contiver a "
    "resposta, diga isso explicitamente em vez de inventar informações."
)

WEB_SYSTEM_PROMPT = (
    "Você é um assistente que responde perguntas fora do escopo de "
    "produtos Getnet usando resultados de busca na web fornecidos como "
    "contexto. Seja claro e direto, e baseie-se apenas no contexto dado."
)

NO_ANSWER_MESSAGE = (
    "Não encontrei informações suficientes para responder a essa pergunta "
    "com segurança. Você pode reformular a pergunta ou pedir para falar "
    "com um atendente humano."
)

RELEVANCE_THRESHOLD = 0.75


class GeneratorProtocol(Protocol):
    async def generate(self, system_prompt: str, question: str, context: str): ...


class KnowledgeAgent:
    """RAG over the ingested Getnet corpus, falling back to Tavily web
    search when retrieval finds nothing relevant enough (i.e. the
    question is out of the corpus's scope)."""

    def __init__(
        self,
        retrieval_tool: PineconeRetrievalTool,
        web_search_tool: TavilyWebSearchTool,
        generator: GeneratorProtocol,
        relevance_threshold: float = RELEVANCE_THRESHOLD,
        top_k: int = 4,
        disabled_features: list[str] | None = None,
    ):
        self._retrieval_tool = retrieval_tool
        self._web_search_tool = web_search_tool
        self._generator = generator
        self._relevance_threshold = relevance_threshold
        self._top_k = top_k
        self._disabled_features = set(disabled_features or [])

    async def handle(self, message: str, user_id: str) -> AgentResult:
        usage: list[UsageRecord] = []
        tools_used: list[str] = []

        passages = await self._retrieval_tool.search(message, top_k=self._top_k)
        tools_used.append(self._retrieval_tool.name)
        relevant = [p for p in passages if p.score >= self._relevance_threshold]

        if relevant:
            context = "\n\n".join(f"[{p.source_url}]\n{p.text}" for p in relevant)
            generation = await self._generator.generate(RAG_SYSTEM_PROMPT, message, context)
            usage.append(_generation_usage("knowledge.rag_generate", message, generation))
            sources = _dedupe_sources(
                [{"url": p.source_url, "title": p.topic} for p in relevant]
            )
            return AgentResult(
                response=generation.text,
                agent_used="knowledge",
                intent="knowledge",
                sources=sources,
                tools_used=tools_used,
                usage=usage,
            )

        if self._web_search_tool.name in self._disabled_features:
            return AgentResult(
                response=NO_ANSWER_MESSAGE,
                agent_used="knowledge",
                intent="knowledge",
                sources=[],
                tools_used=tools_used,
                usage=usage,
            )

        web_results = await self._web_search_tool.search(message, max_results=self._top_k)
        tools_used.append(self._web_search_tool.name)

        if not web_results:
            return AgentResult(
                response=NO_ANSWER_MESSAGE,
                agent_used="knowledge",
                intent="knowledge",
                sources=[],
                tools_used=tools_used,
                usage=usage,
            )

        context = "\n\n".join(f"[{r.url}] {r.title}\n{r.content}" for r in web_results)
        generation = await self._generator.generate(WEB_SYSTEM_PROMPT, message, context)
        usage.append(_generation_usage("knowledge.web_generate", message, generation))
        sources = _dedupe_sources([{"url": r.url, "title": r.title} for r in web_results])

        return AgentResult(
            response=generation.text,
            agent_used="knowledge",
            intent="knowledge",
            sources=sources,
            tools_used=tools_used,
            usage=usage,
        )


def _generation_usage(step: str, message: str, generation) -> UsageRecord:
    return UsageRecord(
        step=step,
        model=generation.model,
        input_data=message,
        output_data=generation.text,
        prompt_tokens=generation.prompt_tokens,
        completion_tokens=generation.completion_tokens,
        latency_ms=generation.latency_ms,
        status="truncated" if getattr(generation, "truncated", False) else "ok",
    )


def _dedupe_sources(sources: list[dict]) -> list[dict]:
    seen: set[str] = set()
    deduped = []
    for source in sources:
        if source["url"] in seen:
            continue
        seen.add(source["url"])
        deduped.append(source)
    return deduped
