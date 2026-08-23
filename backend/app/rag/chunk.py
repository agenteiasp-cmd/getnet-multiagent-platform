from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass(frozen=True)
class Chunk:
    text: str
    source_url: str
    topic: str
    chunk_index: int


def chunk_text(text: str, source_url: str, topic: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> list[Chunk]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    pieces = [piece for piece in splitter.split_text(text) if piece.strip()]
    return [
        Chunk(text=piece, source_url=source_url, topic=topic, chunk_index=i)
        for i, piece in enumerate(pieces)
    ]
