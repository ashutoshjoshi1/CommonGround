from typing import Any

from pydantic import BaseModel, Field


class InsightsResponse(BaseModel):
    workspace_id: str
    sentiment: dict[str, Any]
    topics: list[dict[str, Any]]
    keywords: list[dict[str, Any]]
    trends: list[dict[str, Any]]
    document_classification: list[dict[str, Any]]


class FindingsCreate(BaseModel):
    workspace_id: str
    source_id: str | None = None
    run_id: str | None = None
    finding_type: str = "theme"
    title: str
    body: str
    confidence: float = 0.0
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class FindingsResponse(FindingsCreate):
    id: str
    status: str
