from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    id: str
    workspace_id: str | None
    user_id: str | None
    entity_type: str
    entity_id: str | None
    action: str
    details_json: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
