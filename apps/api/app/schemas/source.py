from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SourceResponse(BaseModel):
    id: str
    workspace_id: str
    file_name: str
    file_type: str
    file_size: int
    file_hash: str
    status: str
    metadata_json: dict[str, Any]
    dedupe_hint: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SourceChunkResponse(BaseModel):
    id: str
    source_id: str
    chunk_index: int
    content: str
    page_number: int | None
    metadata_json: dict[str, Any]

    model_config = {"from_attributes": True}


class SourceDetailResponse(SourceResponse):
    preview_text: str | None = None
    chunks: list[SourceChunkResponse] = Field(default_factory=list)


class ReindexRequest(BaseModel):
    force: bool = False
