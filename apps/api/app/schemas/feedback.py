from datetime import datetime

from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    workspace_id: str
    run_id: str | None = None
    rating: int | None = None
    correctness_label: str = "needs-review"
    comments: str | None = None


class FeedbackResponse(BaseModel):
    id: str
    workspace_id: str
    run_id: str | None
    user_id: str
    rating: int | None
    correctness_label: str
    comments: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
