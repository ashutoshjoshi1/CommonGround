from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    workspace_id: str
    query: str = Field(min_length=3)
    top_k: int | None = None
    prompt_version_id: str | None = None


class Citation(BaseModel):
    citation_label: str
    source_id: str
    source_name: str
    chunk_id: str
    rank: int
    score: float
    excerpt: str


class QueryResponse(BaseModel):
    run_id: str
    answer: str
    confidence_label: str
    abstained: bool
    citations: list[Citation]
    retrieved_passages: list[Citation]
    prompt_version_id: str | None
    trace_summary: dict[str, Any]


class RunStepResponse(BaseModel):
    id: str
    step_name: str
    step_order: int
    status: str
    input_json: dict[str, Any]
    output_json: dict[str, Any]
    duration_ms: int | None

    model_config = {"from_attributes": True}


class RetrievedChunkResponse(BaseModel):
    id: str
    source_chunk_id: str
    rank: int
    score: float
    citation_label: str
    excerpt: str

    model_config = {"from_attributes": True}


class RunResponse(BaseModel):
    id: str
    workspace_id: str
    query: str
    answer: str | None
    status: str
    confidence_label: str
    abstained: bool
    provider: str | None
    model_name: str | None
    latency_ms: int | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class RunDetailResponse(RunResponse):
    steps: list[RunStepResponse]
    retrieved_chunks: list[RetrievedChunkResponse]
