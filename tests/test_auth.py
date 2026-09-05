def test_register_login_and_me(client):
    payload = {
        "email": "dev@example.com",
        "full_name": "Dev User",
        "password": "VeryStrongPass123!",
        "organization_name": "DevOps Co",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login.status_code == 200

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == payload["email"]


def test_duplicate_registration_rejected(client):
    payload = {
        "email": "dev@example.com",
        "full_name": "Dev User",
        "password": "VeryStrongPass123!",
        "organization_name": "DevOps Co",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409


def test_authenticated_user_can_list_workspaces(client):
    payload = {
        "email": "workspace@example.com",
        "full_name": "Workspace Owner",
        "password": "StrongPass123!",
        "organization_name": "Workspace Co",
    }
    registered = client.post("/api/v1/auth/register", json=payload)
    assert registered.status_code == 201
    token = registered.json()["access_token"]

    response = client.get(
        "/api/v1/auth/workspaces",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Workspace Co"
    assert data[0]["role"] == "owner"
