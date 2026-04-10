import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User, Workspace, WorkspaceMember, WorkspaceRole
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from app.services.audit import log_audit_event

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "workspace"


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Workspace]:
    return (
        db.query(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == current_user.id)
        .order_by(Workspace.updated_at.desc())
        .all()
    )


@router.post("", response_model=WorkspaceResponse)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Workspace:
    slug = _slugify(payload.name)
    existing = db.query(Workspace).filter(Workspace.slug == slug).first()
    if existing:
        slug = f"{slug}-{str(current_user.id)[:8]}"

    workspace = Workspace(
        name=payload.name,
        slug=slug,
        description=payload.description,
        created_by_id=current_user.id,
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    db.add(
        WorkspaceMember(
            workspace_id=workspace.id,
            user_id=current_user.id,
            role=WorkspaceRole.OWNER,
        )
    )
    db.commit()

    log_audit_event(
        db,
        action="workspace.create",
        entity_type="workspace",
        entity_id=workspace.id,
        workspace_id=workspace.id,
        user_id=current_user.id,
        details={"name": workspace.name},
    )

    return workspace


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Workspace:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == current_user.id
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Workspace access denied")

    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: str,
    payload: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Workspace:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == current_user.id
        )
        .first()
    )
    if not membership or membership.role not in {WorkspaceRole.OWNER, WorkspaceRole.EDITOR}:
        raise HTTPException(status_code=403, detail="Workspace edit denied")

    if payload.name is not None:
        workspace.name = payload.name
    if payload.description is not None:
        workspace.description = payload.description

    db.commit()
    db.refresh(workspace)

    log_audit_event(
        db,
        action="workspace.update",
        entity_type="workspace",
        entity_id=workspace.id,
        workspace_id=workspace.id,
        user_id=current_user.id,
    )

    return workspace
