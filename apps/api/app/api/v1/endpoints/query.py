from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import ensure_workspace_access, get_current_user
from app.db.session import get_db
from app.models import RetrievedChunk, Run, RunStep, User
from app.schemas.query import (
    QueryRequest,
    QueryResponse,
    RunDetailResponse,
    RunResponse,
)
from app.services.audit import log_audit_event
from app.services.query_runner import run_query_pipeline

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def query_workspace(
    payload: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QueryResponse:
    ensure_workspace_access(db, current_user.id, payload.workspace_id)

    result = run_query_pipeline(
        db=db,
        workspace_id=payload.workspace_id,
        user_id=current_user.id,
        query=payload.query,
        prompt_version_id=payload.prompt_version_id,
        top_k=payload.top_k,
    )

    run = result["run"]
    log_audit_event(
        db,
        action="query.run",
        entity_type="run",
        entity_id=run.id,
        workspace_id=payload.workspace_id,
        user_id=current_user.id,
        details={"query": payload.query[:200], "abstained": run.abstained},
    )

    return QueryResponse(
        run_id=run.id,
        answer=run.answer or "",
        confidence_label=run.confidence_label,
        abstained=run.abstained,
        citations=result["citations"],
        retrieved_passages=result["citations"],
        prompt_version_id=run.prompt_version_id,
        trace_summary=result["trace"],
    )


@router.get("/runs", response_model=list[RunResponse])
def list_runs(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Run]:
    ensure_workspace_access(db, current_user.id, workspace_id)
    return (
        db.query(Run)
        .filter(Run.workspace_id == workspace_id)
        .order_by(Run.created_at.desc())
        .limit(100)
        .all()
    )


@router.get("/runs/{run_id}", response_model=RunDetailResponse)
def get_run_detail(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunDetailResponse:
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    ensure_workspace_access(db, current_user.id, run.workspace_id)

    steps = (
        db.query(RunStep).filter(RunStep.run_id == run.id).order_by(RunStep.step_order.asc()).all()
    )
    retrieved = (
        db.query(RetrievedChunk)
        .filter(RetrievedChunk.run_id == run.id)
        .order_by(RetrievedChunk.rank.asc())
        .all()
    )

    return RunDetailResponse(
        id=run.id,
        workspace_id=run.workspace_id,
        query=run.query,
        answer=run.answer,
        status=run.status.value if hasattr(run.status, "value") else str(run.status),
        confidence_label=run.confidence_label,
        abstained=run.abstained,
        provider=run.provider,
        model_name=run.model_name,
        latency_ms=run.latency_ms,
        created_at=run.created_at,
        completed_at=run.completed_at,
        steps=steps,
        retrieved_chunks=retrieved,
    )
