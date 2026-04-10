from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PromptCreate(BaseModel):
    workspace_id: str
    name: str
    description: str | None = None
    template: str
    model_name: str = "local-extractive"
    provider: str = "local"
    settings_json: dict[str, Any] = Field(default_factory=dict)


class PromptVersionCreate(BaseModel):
    template: str
    model_name: str = "local-extractive"
    provider: str = "local"
    settings_json: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = False
    is_default: bool = False


class PromptResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: str | None
    is_archived: bool
    created_by_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromptVersionResponse(BaseModel):
    id: str
    prompt_id: str
    version_number: int
    template: str
    model_name: str
    provider: str
    settings_json: dict[str, Any]
    is_active: bool
    is_default: bool
    created_by_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PromptComparisonRequest(BaseModel):
    workspace_id: str
    query: str
    prompt_version_ids: list[str]
