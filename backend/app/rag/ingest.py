import asyncio
from pathlib import Path

import httpx
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from app.config import get_settings
from app.rag.chunk import Chunk, chunk_text
from app.rag.corpus_sources import CORPUS_SOURCES
from app.rag.fetch import fetch_page_text
from app.rag.manifest import ManifestEntry, now_iso, write_manifest

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

MANIFEST_PATH = Path(__file__).resolve().parent.parent.parent / "data_store" / "rag_manifest.json"


async def fetch_all_chunks(
    client: httpx.AsyncClient | None = None,
) -> dict[str, list[Chunk]]:
    """Fetch every corpus source and chunk it. Pure fetch+chunk step, kept
    separate from embedding/upsert so it's testable without hitting
    Pinecone/OpenAI."""
    owns_client = client is None
    client = client or httpx.AsyncClient(timeout=30.0)
    try:
        result: dict[str, list[Chunk]] = {}
        for source in CORPUS_SOURCES:
            text = await fetch_page_text(source.url, client)
            result[source.url] = chunk_text(text, source.url, source.topic)
        return result
    finally:
        if owns_client:
            await client.aclose()


def ensure_index(pc: Pinecone, index_name: str):
    existing_names = {idx["name"] for idx in pc.list_indexes()}
    if index_name not in existing_names:
        pc.create_index(
            name=index_name,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return pc.Index(index_name)


def run_ingestion() -> list[ManifestEntry]:
    """Full pipeline: fetch -> chunk -> embed -> upsert to Pinecone ->
    write the ingestion manifest consumed by the README."""
    settings = get_settings()

    chunks_by_source = asyncio.run(fetch_all_chunks())

    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = ensure_index(pc, settings.pinecone_index_name)
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=settings.openai_api_key)
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    ingested_date = now_iso()
    manifest_entries: list[ManifestEntry] = []
    for source in CORPUS_SOURCES:
        chunks = chunks_by_source.get(source.url, [])
        if not chunks:
            continue
        vector_store.add_texts(
            texts=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "source_url": chunk.source_url,
                    "topic": chunk.topic,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in chunks
            ],
        )
        manifest_entries.append(
            ManifestEntry(
                url=source.url,
                topic=source.topic,
                ingested_at=ingested_date,
                chunk_count=len(chunks),
            )
        )

    write_manifest(manifest_entries, MANIFEST_PATH)
    return manifest_entries


if __name__ == "__main__":
    for entry in run_ingestion():
        print(f"{entry.url}: {entry.chunk_count} chunks ({entry.ingested_at})")
