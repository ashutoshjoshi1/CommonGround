from fastapi.testclient import TestClient


def _create_workspace(client: TestClient, token: str) -> str:
    response = client.post(
        "/api/v1/workspaces",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "People Ops Flow", "description": "Flow test"},
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_upload_and_query_flow(client: TestClient, token: str) -> None:
    workspace_id = _create_workspace(client, token)

    payload = b"Employee survey indicates recurring concerns around onboarding clarity and manager response times."

    upload = client.post(
        f"/api/v1/sources/upload?workspace_id={workspace_id}",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("survey.txt", payload, "text/plain")},
    )
    assert upload.status_code == 200
    source = upload.json()
    assert source["status"] == "ready"

    query = client.post(
        "/api/v1/query",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "workspace_id": workspace_id,
            "query": "What recurring concerns were identified?",
            "top_k": 5,
        },
    )
    assert query.status_code == 200
    data = query.json()
    assert data["run_id"]
    assert isinstance(data["citations"], list)
    assert len(data["citations"]) >= 1

    audit = client.get(
        f"/api/v1/audit?workspace_id={workspace_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert audit.status_code == 200
    assert len(audit.json()) >= 2
