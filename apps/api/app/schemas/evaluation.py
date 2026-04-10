from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EvaluationItemInput(BaseModel):
    query: str
    expected_answer: str | None = None


class EvaluationCreate(BaseModel):
    workspace_id: str
    name: str
    description: str | None = None
    prompt_version_id: str | None = None
    config_json: dict[str, Any] = Field(default_factory=dict)
    items: list[EvaluationItemInput]


class EvaluationResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: str | None
    status: str
    prompt_version_id: str | None
    config_json: dict[str, Any]
    summary_json: dict[str, Any]
    created_by_id: str
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class EvaluationItemResponse(BaseModel):
    id: str
    evaluation_id: str
    query: str
    expected_answer: str | None
    run_id: str | None
    score_groundedness: float | None
    score_citation_coverage: float | None
    score_retrieval_relevance: float | None
    hallucination_risk: float | None
    latency_ms: int | None
    passed: bool | None
    notes: str | None

    model_config = {"from_attributes": True}


class EvaluationDetailResponse(EvaluationResponse):
    items: list[EvaluationItemResponse]


class EvaluationCompareRequest(BaseModel):
    evaluation_id: str
    prompt_version_ids: list[str]
