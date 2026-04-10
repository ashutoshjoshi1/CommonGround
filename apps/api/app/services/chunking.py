from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass
class ChunkResult:
    chunk_index: int
    content: str
    start_char: int
    end_char: int


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[ChunkResult]:
    if not text.strip():
        return []

    size = chunk_size or settings.chunk_size
    overlap = chunk_overlap or settings.chunk_overlap

    chunks: list[ChunkResult] = []
    start = 0
    idx = 0

    while start < len(text):
        end = min(start + size, len(text))
        content = text[start:end].strip()
        if content:
            chunks.append(
                ChunkResult(
                    chunk_index=idx,
                    content=content,
                    start_char=start,
                    end_char=end,
                )
            )
            idx += 1
        if end >= len(text):
            break
        start = max(0, end - overlap)

    return chunks
