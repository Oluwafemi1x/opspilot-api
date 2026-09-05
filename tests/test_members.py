def _register(client):
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": "team@example.com",
            "full_name": "Team Owner",
            "password": "StrongPass123!",
            "organization_name": "Team Ops",
        },
    )
    token = registered.json()["access_token"]
    workspaces = client.get(
        "/api/v1/auth/workspaces",
        headers={"Authorization": f"Bearer {token}"},
    ).json()
    return token, workspaces[0]["id"]


def test_owner_can_list_team_members(client):
    token, org_id = _register(client)
    response = client.get(
        "/api/v1/members",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-ID": org_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Team Owner"
    assert data[0]["role"] == "owner"
