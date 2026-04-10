from sqlalchemy.orm import Session

from app.core.security import create_password_hash
from app.models import Prompt, PromptVersion, User, Workspace, WorkspaceMember


def seed_defaults(db: Session) -> None:
    user = db.query(User).filter(User.email == "demo@example.com").first()
    if user:
        return

    user = User(
        email="demo@example.com",
        full_name="CommonGround Demo",
        password_hash=create_password_hash("password123"),
        is_admin=True,
    )
    db.add(user)
    db.flush()

    workspace = Workspace(
        name="People Strategy",
        slug="people-strategy",
        description="Baseline workspace seeded for local development.",
        created_by_id=user.id,
    )
    db.add(workspace)
    db.flush()

    db.add(WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner"))

    prompt = Prompt(
        workspace_id=workspace.id,
        name="Grounded synthesis",
        description="Default practical grounded response template.",
        created_by_id=user.id,
    )
    db.add(prompt)
    db.flush()

    db.add(
        PromptVersion(
            prompt_id=prompt.id,
            version_number=1,
            template=(
                "You are writing concise internal findings. Only use provided sources. "
                "If evidence is weak, clearly abstain and request additional source coverage."
            ),
            model_name="local-extractive",
            provider="local",
            is_active=True,
            is_default=True,
            created_by_id=user.id,
        )
    )

    db.commit()
