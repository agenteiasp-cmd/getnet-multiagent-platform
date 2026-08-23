from dataclasses import dataclass
from typing import Protocol


@dataclass
class RetrievedPassage:
    text: str
    source_url: str
    topic: str
    score: float


class VectorStoreProtocol(Protocol):
    async def asimilarity_search_with_score(self, query: str, k: int): ...


class PineconeRetrievalTool:
    """Thin wrapper over a LangChain vector store's similarity search, so
    the Knowledge Agent depends on this small interface instead of the
    LangChain/Pinecone SDK directly (easy to fake in tests)."""

    name = "pinecone_retrieval"

    def __init__(self, vector_store: VectorStoreProtocol):
        self._vector_store = vector_store

    async def search(self, query: str, top_k: int = 4) -> list[RetrievedPassage]:
        results = await self._vector_store.asimilarity_search_with_score(query, k=top_k)
        return [
            RetrievedPassage(
                text=doc.page_content,
                source_url=doc.metadata.get("source_url", ""),
                topic=doc.metadata.get("topic", ""),
                score=score,
            )
            for doc, score in results
        ]
