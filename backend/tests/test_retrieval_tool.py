from types import SimpleNamespace

from app.tools.retrieval import PineconeRetrievalTool


class FakeVectorStore:
    def __init__(self, docs_and_scores):
        self._docs_and_scores = docs_and_scores

    async def asimilarity_search_with_score(self, query: str, k: int):
        return self._docs_and_scores[:k]


async def test_retrieval_returns_passages_with_source_urls():
    doc = SimpleNamespace(
        page_content="Get Clássica custa R$ 79,90 por mês.",
        metadata={"source_url": "https://site.getnet.com.br/maquininha/get-classica/", "topic": "get-classica"},
    )
    vector_store = FakeVectorStore([(doc, 0.92)])
    tool = PineconeRetrievalTool(vector_store)

    passages = await tool.search("qual o preço da get classica", top_k=4)

    assert len(passages) == 1
    assert passages[0].source_url == "https://site.getnet.com.br/maquininha/get-classica/"
    assert "Get Clássica" in passages[0].text
    assert passages[0].score == 0.92


async def test_retrieval_respects_top_k():
    docs = [
        (SimpleNamespace(page_content=f"trecho {i}", metadata={"source_url": "u", "topic": "t"}), 1.0)
        for i in range(5)
    ]
    tool = PineconeRetrievalTool(FakeVectorStore(docs))

    passages = await tool.search("query", top_k=2)

    assert len(passages) == 2
