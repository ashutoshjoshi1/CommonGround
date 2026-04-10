from pydantic import BaseModel


class WorkspaceSettingUpdate(BaseModel):
    key: str
    value_json: dict


class WorkspaceSettingResponse(BaseModel):
    id: str
    workspace_id: str
    key: str
    value_json: dict

    model_config = {"from_attributes": True}
