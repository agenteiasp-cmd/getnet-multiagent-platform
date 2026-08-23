from dataclasses import dataclass
from typing import Protocol


@dataclass
class WebSearchResult:
    title: str
    url: str
    content: str


class TavilyClientProtocol(Protocol):
    async def search(self, query: str, max_results: int): ...


class TavilyWebSearchTool:
    """Wraps Tavily's async search client for the Knowledge Agent's
    out-of-scope fallback path."""

    name = "tavily_web_search"

    def __init__(self, client: TavilyClientProtocol):
        self._client = client

    async def search(self, query: str, max_results: int = 4) -> list[WebSearchResult]:
        response = await self._client.search(query=query, max_results=max_results)
        results = response.get("results", []) if isinstance(response, dict) else response
        return [
            WebSearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=item.get("content", ""),
            )
            for item in results
        ]
