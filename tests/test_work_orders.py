def test_work_order_filtering_and_validation(client, auth_context):
    headers = auth_context["headers"]
    client_record = client.post(
        "/api/v1/clients",
        headers=headers,
        json={"name": "Contoso"},
    )
    client_id = client_record.json()["id"]

    work = client.post(
        "/api/v1/work-orders",
        headers=headers,
        json={
            "title": "Repair payment webhook",
            "client_id": client_id,
            "priority": "urgent",
        },
    )
    assert work.status_code == 201
    work_id = work.json()["id"]

    done = client.patch(
        f"/api/v1/work-orders/{work_id}",
        headers=headers,
        json={"status": "completed"},
    )
    assert done.status_code == 200

    filtered = client.get(
        "/api/v1/work-orders?status=completed&priority=urgent",
        headers=headers,
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1


def test_tenant_header_required(client, auth_context):
    headers = {"Authorization": auth_context["headers"]["Authorization"]}
    assert client.get("/api/v1/work-orders", headers=headers).status_code == 422
