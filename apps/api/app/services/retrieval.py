from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Source, SourceChunk, SourceStatus
from app.services.embeddings import cosine_similarity, get_embedding_service


@dataclass
class RetrievedPassage:
    chunk: SourceChunk
    source: Source
    score: float
    rank: int


class RetrievalService:
    def retrieve(
        self, db: Session, workspace_id: str, query: str, top_k: int
    ) -> list[RetrievedPassage]:
        embedder = get_embedding_service()
        query_vector = embedder.embed_texts([query])[0]

        rows = (
            db.query(SourceChunk, Source)
            .join(Source, Source.id == SourceChunk.source_id)
            .filter(Source.workspace_id == workspace_id, Source.status == SourceStatus.READY)
            .all()
        )

        scored: list[RetrievedPassage] = []
        for chunk, source in rows:
            embedding = chunk.embedding
            if isinstance(embedding, str):
                continue
            if isinstance(embedding, dict):
                continue
            score = cosine_similarity(query_vector, list(embedding))
            scored.append(RetrievedPassage(chunk=chunk, source=source, score=float(score), rank=0))

        scored.sort(key=lambda item: item.score, reverse=True)
        top = scored[: max(1, top_k)]
        for idx, item in enumerate(top):
            item.rank = idx + 1
        return top
