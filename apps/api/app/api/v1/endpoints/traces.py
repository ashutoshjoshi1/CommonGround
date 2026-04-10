from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import ensure_workspace_access, get_current_user
from app.db.session import get_db
from app.models import RetrievedChunk, Run, RunStep, User

router = APIRouter(prefix="/traces", tags=["traces"])


@router.get("/{run_id}")
def get_trace(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
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

    return {
        "run": {
            "id": run.id,
            "query": run.query,
            "status": run.status,
            "model_name": run.model_name,
            "provider": run.provider,
            "latency_ms": run.latency_ms,
            "created_at": run.created_at,
            "completed_at": run.completed_at,
        },
        "steps": [
            {
                "name": step.step_name,
                "order": step.step_order,
                "status": step.status,
                "duration_ms": step.duration_ms,
                "input": step.input_json,
                "output": step.output_json,
            }
            for step in steps
        ],
        "retrieved_chunks": [
            {
                "chunk_id": row.source_chunk_id,
                "rank": row.rank,
                "score": row.score,
                "citation_label": row.citation_label,
                "excerpt": row.excerpt,
            }
            for row in retrieved
        ],
    }
