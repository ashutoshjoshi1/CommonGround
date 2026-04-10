from fastapi.testclient import TestClient


def _create_workspace(client: TestClient, token: str) -> str:
    response = client.post(
        "/api/v1/workspaces",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Prompt Eval", "description": "Prompt eval workspace"},
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_prompt_and_evaluation(client: TestClient, token: str) -> None:
    workspace_id = _create_workspace(client, token)

    upload = client.post(
        f"/api/v1/sources/upload?workspace_id={workspace_id}",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                "notes.txt",
                b"Interview notes: concern themes include workload equity and unclear ownership boundaries.",
                "text/plain",
            )
        },
    )
    assert upload.status_code == 200

    prompt = client.post(
        "/api/v1/prompts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "workspace_id": workspace_id,
            "name": "Evidence-first",
            "description": "Strict grounding",
            "template": "Respond only with grounded findings and abstain otherwise.",
            "model_name": "local-extractive",
            "provider": "local",
            "settings_json": {},
        },
    )
    assert prompt.status_code == 200
    prompt_version_id = prompt.json()["id"]

    evaluation = client.post(
        "/api/v1/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "workspace_id": workspace_id,
            "name": "Regression set",
            "description": "Baseline check",
            "prompt_version_id": prompt_version_id,
            "config_json": {"top_k": 5, "pass_threshold": 0.5},
            "items": [
                {"query": "What concern themes are present?", "expected_answer": "workload equity"},
                {
                    "query": "Which boundaries are unclear?",
                    "expected_answer": "ownership boundaries",
                },
            ],
        },
    )
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["id"]

    run = client.post(
        f"/api/v1/evaluations/{evaluation_id}/run",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert run.status_code == 200
    assert run.json()["status"] == "completed"
