from fastapi.testclient import TestClient


def test_login_and_me(client: TestClient) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "demo@example.com"


def test_create_workspace(client: TestClient, token: str) -> None:
    create = client.post(
        "/api/v1/workspaces",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Operations Review", "description": "Ops docs"},
    )
    assert create.status_code == 200

    listing = client.get(
        "/api/v1/workspaces",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listing.status_code == 200
    assert any(item["name"] == "Operations Review" for item in listing.json())
