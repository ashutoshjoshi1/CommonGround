from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import ensure_workspace_access, get_current_user
from app.db.session import get_db
from app.models import Prompt, PromptVersion, User
from app.schemas.prompt import (
    PromptComparisonRequest,
    PromptCreate,
    PromptResponse,
    PromptVersionCreate,
    PromptVersionResponse,
)
from app.services.audit import log_audit_event
from app.services.query_runner import run_query_pipeline

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("", response_model=list[PromptResponse])
def list_prompts(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Prompt]:
    ensure_workspace_access(db, current_user.id, workspace_id)
    return (
        db.query(Prompt)
        .filter(Prompt.workspace_id == workspace_id, Prompt.is_archived.is_(False))
        .order_by(Prompt.updated_at.desc())
        .all()
    )


@router.post("", response_model=PromptVersionResponse)
def create_prompt(
    payload: PromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptVersion:
    ensure_workspace_access(db, current_user.id, payload.workspace_id)

    prompt = Prompt(
        workspace_id=payload.workspace_id,
        name=payload.name,
        description=payload.description,
        created_by_id=current_user.id,
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    prompt_version = PromptVersion(
        prompt_id=prompt.id,
        version_number=1,
        template=payload.template,
        model_name=payload.model_name,
        provider=payload.provider,
        settings_json=payload.settings_json,
        is_active=True,
        is_default=False,
        created_by_id=current_user.id,
    )
    db.add(prompt_version)
    db.commit()
    db.refresh(prompt_version)

    log_audit_event(
        db,
        action="prompt.create",
        entity_type="prompt",
        entity_id=prompt.id,
        workspace_id=payload.workspace_id,
        user_id=current_user.id,
    )

    return prompt_version


@router.get("/{prompt_id}/versions", response_model=list[PromptVersionResponse])
def list_prompt_versions(
    prompt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PromptVersion]:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    ensure_workspace_access(db, current_user.id, prompt.workspace_id)

    return (
        db.query(PromptVersion)
        .filter(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version_number.desc())
        .all()
    )


@router.post("/{prompt_id}/versions", response_model=PromptVersionResponse)
def create_prompt_version(
    prompt_id: str,
    payload: PromptVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptVersion:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    ensure_workspace_access(db, current_user.id, prompt.workspace_id)

    last = (
        db.query(PromptVersion)
        .filter(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version_number.desc())
        .first()
    )

    version_number = 1 if last is None else last.version_number + 1

    if payload.is_default:
        db.query(PromptVersion).filter(PromptVersion.prompt_id == prompt_id).update(
            {PromptVersion.is_default: False}
        )
    if payload.is_active:
        db.query(PromptVersion).filter(PromptVersion.prompt_id == prompt_id).update(
            {PromptVersion.is_active: False}
        )

    version = PromptVersion(
        prompt_id=prompt_id,
        version_number=version_number,
        template=payload.template,
        model_name=payload.model_name,
        provider=payload.provider,
        settings_json=payload.settings_json,
        is_active=payload.is_active,
        is_default=payload.is_default,
        created_by_id=current_user.id,
    )
    db.add(version)
    db.commit()
    db.refresh(version)

    log_audit_event(
        db,
        action="prompt.version.create",
        entity_type="prompt_version",
        entity_id=version.id,
        workspace_id=prompt.workspace_id,
        user_id=current_user.id,
    )

    return version


@router.post("/compare")
def compare_prompt_versions(
    payload: PromptComparisonRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    ensure_workspace_access(db, current_user.id, payload.workspace_id)

    comparisons = []
    for prompt_version_id in payload.prompt_version_ids:
        result = run_query_pipeline(
            db=db,
            workspace_id=payload.workspace_id,
            user_id=current_user.id,
            query=payload.query,
            prompt_version_id=prompt_version_id,
            top_k=6,
        )
        run = result["run"]
        comparisons.append(
            {
                "prompt_version_id": prompt_version_id,
                "run_id": run.id,
                "answer": run.answer,
                "confidence_label": run.confidence_label,
                "abstained": run.abstained,
                "citations": result["citations"],
            }
        )

    return {"comparisons": comparisons}
