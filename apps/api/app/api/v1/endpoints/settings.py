from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import ensure_workspace_access, get_current_user
from app.db.session import get_db
from app.models import User, WorkspaceSetting
from app.schemas.settings import WorkspaceSettingResponse, WorkspaceSettingUpdate
from app.services.audit import log_audit_event

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/{workspace_id}", response_model=list[WorkspaceSettingResponse])
def list_workspace_settings(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WorkspaceSetting]:
    ensure_workspace_access(db, current_user.id, workspace_id)
    return (
        db.query(WorkspaceSetting)
        .filter(WorkspaceSetting.workspace_id == workspace_id)
        .order_by(WorkspaceSetting.key.asc())
        .all()
    )


@router.post("/{workspace_id}", response_model=WorkspaceSettingResponse)
def upsert_workspace_setting(
    workspace_id: str,
    payload: WorkspaceSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkspaceSetting:
    ensure_workspace_access(db, current_user.id, workspace_id)

    row = (
        db.query(WorkspaceSetting)
        .filter(WorkspaceSetting.workspace_id == workspace_id, WorkspaceSetting.key == payload.key)
        .first()
    )

    if row:
        row.value_json = payload.value_json
        row.updated_by_id = current_user.id
    else:
        row = WorkspaceSetting(
            workspace_id=workspace_id,
            key=payload.key,
            value_json=payload.value_json,
            updated_by_id=current_user.id,
        )
        db.add(row)

    db.commit()
    db.refresh(row)

    log_audit_event(
        db,
        action="settings.upsert",
        entity_type="workspace_setting",
        entity_id=row.id,
        workspace_id=workspace_id,
        user_id=current_user.id,
        details={"key": row.key},
    )

    return row
