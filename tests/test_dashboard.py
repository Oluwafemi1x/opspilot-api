def test_dashboard_summary_starts_empty(client):
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": "dashboard@example.com",
            "full_name": "Dashboard Owner",
            "password": "StrongPass123!",
            "organization_name": "Dashboard Ops",
        },
    )
    token = registered.json()["access_token"]
    org_id = client.get(
        "/api/v1/auth/workspaces",
        headers={"Authorization": f"Bearer {token}"},
    ).json()[0]["id"]
    response = client.get(
        "/api/v1/dashboard/summary",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-ID": org_id,
        },
    )
    assert response.status_code == 200
    assert response.json()["clients"] == 0
    assert response.json()["open_work"] == 0
    assert response.json()["completion_rate"] == 0
