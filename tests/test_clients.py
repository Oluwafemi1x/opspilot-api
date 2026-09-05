def test_client_crud_and_pagination(client, auth_context):
    headers = auth_context["headers"]
    created = client.post(
        "/api/v1/clients",
        headers=headers,
        json={"name": "Northwind Ltd", "email": "ops@northwind.example"},
    )
    assert created.status_code == 201
    client_id = created.json()["id"]

    listing = client.get(
        "/api/v1/clients?page=1&page_size=10&search=North",
        headers=headers,
    )
    assert listing.status_code == 200
    assert listing.json()["total"] == 1

    updated = client.patch(
        f"/api/v1/clients/{client_id}",
        headers=headers,
        json={"phone": "+2348000000000"},
    )
    assert updated.status_code == 200
    fetched = client.get(f"/api/v1/clients/{client_id}", headers=headers)
    assert fetched.json()["phone"] == "+2348000000000"
