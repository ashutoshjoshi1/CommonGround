from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditEvent


def log_audit_event(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    workspace_id: str | None = None,
    user_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditEvent:
    event = AuditEvent(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        workspace_id=workspace_id,
        user_id=user_id,
        details_json=details or {},
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
