from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.init_db import seed_defaults
from app.db.session import SessionLocal, engine
from app.models import Evaluation, EvaluationItem, Source, User, Workspace
from app.services.ingestion import create_source_record, process_source

DEMO_DOCS: dict[str, str] = {
    "interview-notes.txt": (
        "Interview synthesis:\n"
        "- Managers report uneven onboarding readiness among teams.\n"
        "- New hires mention unclear ownership boundaries in the first 30 days.\n"
        "- Recurring request: clearer escalation channels for cross-team decisions."
    ),
    "policy-summary.txt": (
        "Policy notes:\n"
        "- Response SLA for employee support requests is 3 business days.\n"
        "- Team leads must document role expectations in the first week.\n"
        "- Quarterly review requires evidence-backed trend summaries."
    ),
}


def _load_demo_user_workspace(db: Session) -> tuple[User, Workspace]:
    user = db.query(User).filter(User.email == "demo@example.com").first()
    if not user:
        raise RuntimeError("Demo user missing. Seed defaults should create it.")

    workspace = db.query(Workspace).filter(Workspace.created_by_id == user.id).first()
    if not workspace:
        raise RuntimeError("Seeded workspace missing.")

    return user, workspace


def seed_demo_sources(db: Session, *, user: User, workspace: Workspace) -> None:
    existing_count = db.query(Source).filter(Source.workspace_id == workspace.id).count()
    if existing_count > 0:
        return

    for file_name, content in DEMO_DOCS.items():
        payload = content.encode("utf-8")
        source = create_source_record(
            db,
            workspace_id=workspace.id,
            uploaded_by_id=user.id,
            file_name=file_name,
            payload=payload,
        )
        process_source(db=db, source=source, payload=payload)


def seed_evaluation_set(db: Session, *, user: User, workspace: Workspace) -> None:
    existing_eval = db.query(Evaluation).filter(Evaluation.workspace_id == workspace.id).first()
    if existing_eval:
        return

    evaluation = Evaluation(
        workspace_id=workspace.id,
        name="Starter evaluation",
        description="Seeded internal quality checks",
        config_json={"top_k": 6, "pass_threshold": 0.62},
        created_by_id=user.id,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    items = [
        "What onboarding concerns were mentioned?",
        "What role-clarity expectations are documented?",
        "What are the recurring escalation issues?",
    ]

    for query in items:
        db.add(EvaluationItem(evaluation_id=evaluation.id, query=query))

    db.commit()


def main() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_defaults(db)
        user, workspace = _load_demo_user_workspace(db)
        seed_demo_sources(db, user=user, workspace=workspace)
        seed_evaluation_set(db, user=user, workspace=workspace)
        print("Seed completed for CommonGround demo workspace")
    finally:
        db.close()


if __name__ == "__main__":
    main()
