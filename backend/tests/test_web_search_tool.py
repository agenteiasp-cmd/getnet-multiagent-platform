from app.tools.web_search import TavilyWebSearchTool


class FakeTavilyClient:
    def __init__(self, results):
        self._results = results
        self.calls: list[tuple[str, int]] = []

    async def search(self, query: str, max_results: int):
        self.calls.append((query, max_results))
        return {"results": self._results}


async def test_web_search_returns_results_with_source_urls():
    client = FakeTavilyClient(
        [
            {"title": "Previsão do tempo", "url": "https://weather.example.com/forecast", "content": "Chuva amanhã."},
        ]
    )
    tool = TavilyWebSearchTool(client)

    results = await tool.search("previsão do tempo amanhã")

    assert len(results) == 1
    assert results[0].url == "https://weather.example.com/forecast"
    assert results[0].content == "Chuva amanhã."
    assert client.calls == [("previsão do tempo amanhã", 4)]


async def test_web_search_handles_empty_results():
    client = FakeTavilyClient([])
    tool = TavilyWebSearchTool(client)

    results = await tool.search("query obscura")

    assert results == []
