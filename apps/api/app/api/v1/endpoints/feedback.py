from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import ensure_workspace_access, get_current_user
from app.db.session import get_db
from app.models import Feedback, User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.audit import log_audit_event

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Feedback:
    ensure_workspace_access(db, current_user.id, payload.workspace_id)

    feedback = Feedback(
        workspace_id=payload.workspace_id,
        run_id=payload.run_id,
        user_id=current_user.id,
        rating=payload.rating,
        correctness_label=payload.correctness_label,
        comments=payload.comments,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    log_audit_event(
        db,
        action="feedback.create",
        entity_type="feedback",
        entity_id=feedback.id,
        workspace_id=feedback.workspace_id,
        user_id=current_user.id,
    )

    return feedback


@router.get("", response_model=list[FeedbackResponse])
def list_feedback(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Feedback]:
    ensure_workspace_access(db, current_user.id, workspace_id)
    return (
        db.query(Feedback)
        .filter(Feedback.workspace_id == workspace_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
