from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import ensure_workspace_access, get_current_user
from app.db.session import get_db
from app.models import Evaluation, EvaluationItem, User
from app.schemas.evaluation import (
    EvaluationCompareRequest,
    EvaluationCreate,
    EvaluationDetailResponse,
    EvaluationResponse,
)
from app.services.audit import log_audit_event
from app.services.evaluation import compare_prompt_versions, run_evaluation

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


def _to_detail_response(
    evaluation: Evaluation, items: list[EvaluationItem]
) -> EvaluationDetailResponse:
    return EvaluationDetailResponse(
        id=evaluation.id,
        workspace_id=evaluation.workspace_id,
        name=evaluation.name,
        description=evaluation.description,
        status=evaluation.status.value
        if hasattr(evaluation.status, "value")
        else str(evaluation.status),
        prompt_version_id=evaluation.prompt_version_id,
        config_json=evaluation.config_json,
        summary_json=evaluation.summary_json,
        created_by_id=evaluation.created_by_id,
        created_at=evaluation.created_at,
        completed_at=evaluation.completed_at,
        items=items,
    )


@router.get("", response_model=list[EvaluationResponse])
def list_evaluations(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Evaluation]:
    ensure_workspace_access(db, current_user.id, workspace_id)
    return (
        db.query(Evaluation)
        .filter(Evaluation.workspace_id == workspace_id)
        .order_by(Evaluation.created_at.desc())
        .all()
    )


@router.post("", response_model=EvaluationDetailResponse)
def create_evaluation(
    payload: EvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EvaluationDetailResponse:
    ensure_workspace_access(db, current_user.id, payload.workspace_id)

    evaluation = Evaluation(
        workspace_id=payload.workspace_id,
        name=payload.name,
        description=payload.description,
        prompt_version_id=payload.prompt_version_id,
        config_json=payload.config_json,
        created_by_id=current_user.id,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    items = []
    for item in payload.items:
        row = EvaluationItem(
            evaluation_id=evaluation.id,
            query=item.query,
            expected_answer=item.expected_answer,
        )
        db.add(row)
        items.append(row)

    db.commit()

    log_audit_event(
        db,
        action="evaluation.create",
        entity_type="evaluation",
        entity_id=evaluation.id,
        workspace_id=evaluation.workspace_id,
        user_id=current_user.id,
        details={"item_count": len(items)},
    )

    return _to_detail_response(evaluation, items)


@router.get("/{evaluation_id}", response_model=EvaluationDetailResponse)
def get_evaluation(
    evaluation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EvaluationDetailResponse:
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    ensure_workspace_access(db, current_user.id, evaluation.workspace_id)

    items = (
        db.query(EvaluationItem)
        .filter(EvaluationItem.evaluation_id == evaluation.id)
        .order_by(EvaluationItem.created_at.asc())
        .all()
    )

    return _to_detail_response(evaluation, items)


@router.post("/{evaluation_id}/run", response_model=EvaluationDetailResponse)
def run_evaluation_endpoint(
    evaluation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EvaluationDetailResponse:
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    ensure_workspace_access(db, current_user.id, evaluation.workspace_id)

    evaluation = run_evaluation(db, evaluation)

    items = (
        db.query(EvaluationItem)
        .filter(EvaluationItem.evaluation_id == evaluation.id)
        .order_by(EvaluationItem.created_at.asc())
        .all()
    )

    log_audit_event(
        db,
        action="evaluation.run",
        entity_type="evaluation",
        entity_id=evaluation.id,
        workspace_id=evaluation.workspace_id,
        user_id=current_user.id,
    )

    return _to_detail_response(evaluation, items)


@router.post("/compare")
def compare_evaluation_prompts(
    payload: EvaluationCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    evaluation = db.query(Evaluation).filter(Evaluation.id == payload.evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    ensure_workspace_access(db, current_user.id, evaluation.workspace_id)
    return {
        "evaluation_id": evaluation.id,
        "comparison": compare_prompt_versions(
            db=db,
            evaluation=evaluation,
            prompt_version_ids=payload.prompt_version_ids,
        ),
    }


@router.get("/{evaluation_id}/export")
def export_evaluation_report(
    evaluation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    ensure_workspace_access(db, current_user.id, evaluation.workspace_id)

    items = (
        db.query(EvaluationItem)
        .filter(EvaluationItem.evaluation_id == evaluation_id)
        .order_by(EvaluationItem.created_at.asc())
        .all()
    )

    return {
        "evaluation": {
            "id": evaluation.id,
            "name": evaluation.name,
            "status": evaluation.status,
            "summary": evaluation.summary_json,
        },
        "items": [
            {
                "query": item.query,
                "expected_answer": item.expected_answer,
                "scores": {
                    "groundedness": item.score_groundedness,
                    "citation_coverage": item.score_citation_coverage,
                    "retrieval_relevance": item.score_retrieval_relevance,
                    "hallucination_risk": item.hallucination_risk,
                },
                "passed": item.passed,
                "notes": item.notes,
            }
            for item in items
        ],
    }
