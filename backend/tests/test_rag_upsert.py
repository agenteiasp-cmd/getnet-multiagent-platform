from unittest.mock import MagicMock

import pytest

from app.rag import ingest
from app.rag.chunk import Chunk
from app.rag.corpus_sources import CORPUS_SOURCES
from app.rag.manifest import read_manifest


async def _fake_chunks_by_source():
    return {source.url: [Chunk(text=f"conteúdo de {source.topic}", source_url=source.url, topic=source.topic, chunk_index=0)] for source in CORPUS_SOURCES}


def test_run_ingestion_upserts_expected_vector_count_to_mock_index(monkeypatch, tmp_path):
    async def fake_fetch_all_chunks(client=None):
        return await _fake_chunks_by_source()

    monkeypatch.setattr(ingest, "fetch_all_chunks", fake_fetch_all_chunks)

    fake_settings = MagicMock(
        pinecone_api_key="pc-test",
        pinecone_index_name="test-index",
        openai_api_key="sk-test",
    )
    monkeypatch.setattr(ingest, "get_settings", lambda: fake_settings)

    fake_index = MagicMock()
    fake_pinecone_client = MagicMock()
    fake_pinecone_client.list_indexes.return_value = []
    fake_pinecone_client.Index.return_value = fake_index
    monkeypatch.setattr(ingest, "Pinecone", MagicMock(return_value=fake_pinecone_client))

    added_texts: list[list[str]] = []

    class FakeVectorStore:
        def __init__(self, index, embedding):
            pass

        def add_texts(self, texts, metadatas):
            added_texts.append(texts)

    monkeypatch.setattr(ingest, "PineconeVectorStore", FakeVectorStore)
    monkeypatch.setattr(ingest, "OpenAIEmbeddings", MagicMock())
    manifest_path = tmp_path / "rag_manifest.json"
    monkeypatch.setattr(ingest, "MANIFEST_PATH", manifest_path)

    entries = ingest.run_ingestion()

    fake_pinecone_client.create_index.assert_called_once()
    total_upserted = sum(len(texts) for texts in added_texts)
    assert total_upserted == len(CORPUS_SOURCES)
    assert len(entries) == len(CORPUS_SOURCES)

    manifest_entries = read_manifest(manifest_path)
    assert len(manifest_entries) == len(CORPUS_SOURCES)
    assert {e.url for e in manifest_entries} == {s.url for s in CORPUS_SOURCES}
