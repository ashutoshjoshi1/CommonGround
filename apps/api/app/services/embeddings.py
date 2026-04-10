from __future__ import annotations

import hashlib
import math
from functools import lru_cache

from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(settings.embedding_model)
        except Exception:
            self._model = None
        return self._model

    def _fallback_embed(self, text: str) -> list[float]:
        dim = settings.embedding_dim
        digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
        values = [((digest[i % len(digest)] / 255.0) - 0.5) for i in range(dim)]
        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        return [v / norm for v in values]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        if model is None:
            return [self._fallback_embed(text) for text in texts]

        vectors = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return [list(map(float, vec)) for vec in vectors]


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    numerator = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
    denom_a = math.sqrt(sum(a * a for a in vec_a))
    denom_b = math.sqrt(sum(b * b for b in vec_b))
    if denom_a == 0 or denom_b == 0:
        return 0.0
    return numerator / (denom_a * denom_b)
