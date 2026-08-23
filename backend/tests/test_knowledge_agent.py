from dataclasses import dataclass

from app.agents.knowledge import KnowledgeAgent
from app.tools.retrieval import RetrievedPassage
from app.tools.web_search import WebSearchResult


@dataclass
class FakeGeneration:
    text: str
    model: str = "gpt-4o-mini"
    prompt_tokens: int = 20
    completion_tokens: int = 10
    latency_ms: float = 15.0


class FakeGenerator:
    def __init__(self, text: str):
        self._text = text
        self.calls: list[tuple[str, str, str]] = []

    async def generate(self, system_prompt: str, question: str, context: str):
        self.calls.append((system_prompt, question, context))
        return FakeGeneration(text=self._text)


class FakeRetrievalTool:
    name = "pinecone_retrieval"

    def __init__(self, passages: list[RetrievedPassage]):
        self._passages = passages

    async def search(self, query: str, top_k: int = 4):
        return self._passages


class FakeWebSearchTool:
    name = "tavily_web_search"

    def __init__(self, results: list[WebSearchResult]):
        self._results = results
        self.calls: list[str] = []

    async def search(self, query: str, max_results: int = 4):
        self.calls.append(query)
        return self._results


async def test_in_scope_question_answered_from_rag_with_sources():
    passages = [
        RetrievedPassage(
            text="Get Clássica custa R$ 79,90/mês. Get Smart custa R$ 129,90/mês e tem tela touch.",
            source_url="https://site.getnet.com.br/maquininha/get-classica/",
            topic="get-classica",
            score=0.91,
        )
    ]
    generator = FakeGenerator("A Get Clássica é mais simples; a Get Smart tem tela touch e custa mais.")
    web_tool = FakeWebSearchTool([])
    agent = KnowledgeAgent(FakeRetrievalTool(passages), web_tool, generator)

    result = await agent.handle("qual a diferença entre Get Clássica e Get Smart?", "user-1")

    assert result.agent_used == "knowledge"
    assert result.intent == "knowledge"
    assert result.sources == [{"url": "https://site.getnet.com.br/maquininha/get-classica/", "title": "get-classica"}]
    assert "pinecone_retrieval" in result.tools_used
    assert "tavily_web_search" not in result.tools_used
    assert web_tool.calls == []


async def test_antecipacao_question_answered_from_rag():
    passages = [
        RetrievedPassage(
            text="A antecipação de recebíveis permite receber vendas parceladas em 1 dia útil.",
            source_url="https://site.getnet.com.br/get-ajuda-antecipacao-de-venda/como-antecipar-sua-vendas-pelo-app/",
            topic="antecipacao-recebiveis",
            score=0.88,
        )
    ]
    generator = FakeGenerator("Você pode antecipar recebíveis e receber em 1 dia útil, com uma taxa.")
    agent = KnowledgeAgent(FakeRetrievalTool(passages), FakeWebSearchTool([]), generator)

    result = await agent.handle("como funciona a antecipação de recebíveis?", "user-1")

    assert result.sources[0]["url"].endswith("como-antecipar-sua-vendas-pelo-app/")


async def test_out_of_scope_question_falls_back_to_web_search():
    low_relevance_passages = [
        RetrievedPassage(text="conteúdo pouco relevante", source_url="https://site.getnet.com.br/x/", topic="x", score=0.1)
    ]
    web_results = [
        WebSearchResult(title="Previsão do tempo para amanhã", url="https://weather.example.com/sp", content="Chuva à tarde, 22°C.")
    ]
    generator = FakeGenerator("Amanhã deve chover à tarde, com máxima de 22°C.")
    web_tool = FakeWebSearchTool(web_results)
    agent = KnowledgeAgent(FakeRetrievalTool(low_relevance_passages), web_tool, generator)

    result = await agent.handle("qual a previsão do tempo para amanhã?", "user-1")

    assert web_tool.calls == ["qual a previsão do tempo para amanhã?"]
    assert result.sources == [{"url": "https://weather.example.com/sp", "title": "Previsão do tempo para amanhã"}]
    assert "tavily_web_search" in result.tools_used


async def test_no_relevant_knowledge_returns_graceful_fallback_without_fabricating():
    agent = KnowledgeAgent(FakeRetrievalTool([]), FakeWebSearchTool([]), FakeGenerator("não deveria ser usado"))

    result = await agent.handle("pergunta sem resposta em lugar nenhum", "user-1")

    assert result.sources == []
    assert "não encontrei" in result.response.lower() or "não sei" in result.response.lower()


async def test_web_search_disabled_falls_through_to_no_answer_when_rag_finds_nothing():
    web_tool = FakeWebSearchTool([WebSearchResult(title="x", url="https://x", content="x")])
    agent = KnowledgeAgent(
        FakeRetrievalTool([]),
        web_tool,
        FakeGenerator("não deveria ser usado"),
        disabled_features=["tavily_web_search"],
    )

    result = await agent.handle("qual a previsão do tempo para amanhã?", "user-1")

    assert web_tool.calls == []
    assert result.sources == []
    assert "tavily_web_search" not in result.tools_used


async def test_web_search_disabled_does_not_affect_rag_path():
    passages = [
        RetrievedPassage(
            text="Get Clássica custa R$ 79,90/mês.",
            source_url="https://site.getnet.com.br/maquininha/get-classica/",
            topic="get-classica",
            score=0.9,
        )
    ]
    generator = FakeGenerator("A Get Clássica custa R$ 79,90/mês.")
    agent = KnowledgeAgent(
        FakeRetrievalTool(passages), FakeWebSearchTool([]), generator, disabled_features=["tavily_web_search"]
    )

    result = await agent.handle("quanto custa a Get Clássica?", "user-1")

    assert result.sources == [{"url": "https://site.getnet.com.br/maquininha/get-classica/", "title": "get-classica"}]
