import pytest

from app.rag import ingest
from app.rag.corpus_sources import CORPUS_SOURCES

FAKE_PAGE_TEXT = (
    "Getnet oferece maquininhas, link de pagamento e antecipação de "
    "recebíveis para pequenos e médios negócios. " * 20
)


async def test_fetch_all_chunks_produces_non_empty_chunks_for_every_source(monkeypatch):
    async def fake_fetch_page_text(url, client):
        return FAKE_PAGE_TEXT

    monkeypatch.setattr(ingest, "fetch_page_text", fake_fetch_page_text)

    result = await ingest.fetch_all_chunks()

    assert set(result.keys()) == {source.url for source in CORPUS_SOURCES}
    for source in CORPUS_SOURCES:
        chunks = result[source.url]
        assert len(chunks) > 0
        assert all(chunk.text.strip() for chunk in chunks)
        assert all(chunk.source_url == source.url for chunk in chunks)
        assert all(chunk.topic == source.topic for chunk in chunks)
