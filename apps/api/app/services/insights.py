from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Source, SourceChunk, SourceStatus

STOPWORDS = {
    "the",
    "and",
    "that",
    "with",
    "from",
    "this",
    "have",
    "your",
    "will",
    "about",
    "into",
    "their",
    "were",
    "been",
    "which",
    "when",
    "where",
    "what",
    "there",
    "team",
    "teams",
}


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[a-zA-Z]{3,}", text)]


def _sentiment(text: str) -> float:
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        analyzer = SentimentIntensityAnalyzer()
        return float(analyzer.polarity_scores(text).get("compound", 0.0))
    except Exception:
        positives = len(re.findall(r"\b(good|positive|improved|strong|clear)\b", text.lower()))
        negatives = len(re.findall(r"\b(risk|issue|concern|weak|negative|delay)\b", text.lower()))
        total = max(1, positives + negatives)
        return (positives - negatives) / total


def _classification_label(text: str) -> str:
    lowered = text.lower()
    rules = {
        "policy": ["policy", "compliance", "procedure", "standard"],
        "interview": ["interview", "candidate", "hiring", "feedback"],
        "survey": ["survey", "response", "questionnaire"],
        "operations": ["workflow", "operations", "process", "sla"],
        "strategy": ["strategy", "initiative", "objective", "roadmap"],
    }
    for label, keys in rules.items():
        if any(keyword in lowered for keyword in keys):
            return label
    return "general"


def compute_workspace_insights(db: Session, workspace_id: str) -> dict:
    sources = (
        db.query(Source)
        .filter(Source.workspace_id == workspace_id, Source.status == SourceStatus.READY)
        .order_by(Source.created_at.desc())
        .all()
    )

    chunks = (
        db.query(SourceChunk)
        .join(Source, Source.id == SourceChunk.source_id)
        .filter(Source.workspace_id == workspace_id)
        .all()
    )

    joined_text = "\n".join(chunk.content for chunk in chunks)
    tokens = [t for t in _tokenize(joined_text) if t not in STOPWORDS]
    freq = Counter(tokens)

    sentiment_values = [_sentiment(chunk.content) for chunk in chunks] or [0.0]
    avg_sentiment = sum(sentiment_values) / max(1, len(sentiment_values))

    if avg_sentiment > 0.2:
        sentiment_band = "positive"
    elif avg_sentiment < -0.2:
        sentiment_band = "negative"
    else:
        sentiment_band = "mixed"

    topic_buckets: dict[str, int] = defaultdict(int)
    for source in sources:
        label = _classification_label((source.file_name + " " + str(source.metadata_json)).lower())
        topic_buckets[label] += 1

    trend_counts: dict[str, int] = defaultdict(int)
    for source in sources:
        date_key = (
            source.created_at.date().isoformat()
            if isinstance(source.created_at, datetime)
            else "unknown"
        )
        trend_counts[date_key] += 1

    return {
        "workspace_id": workspace_id,
        "sentiment": {
            "average": round(avg_sentiment, 3),
            "band": sentiment_band,
            "documents_analyzed": len(sources),
            "chunks_analyzed": len(chunks),
        },
        "topics": [
            {"topic": key, "count": value, "share": round(value / max(1, len(sources)), 3)}
            for key, value in sorted(topic_buckets.items(), key=lambda kv: kv[1], reverse=True)
        ],
        "keywords": [
            {"keyword": word, "count": count, "weight": round(math.log1p(count), 3)}
            for word, count in freq.most_common(20)
        ],
        "trends": [
            {"date": date, "documents": count}
            for date, count in sorted(trend_counts.items(), key=lambda kv: kv[0])
        ],
        "document_classification": [
            {
                "source_id": source.id,
                "file_name": source.file_name,
                "label": _classification_label(source.file_name),
            }
            for source in sources
        ],
    }
