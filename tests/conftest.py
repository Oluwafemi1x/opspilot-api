import os

os.environ["DATABASE_URL"] = "sqlite:///./test_opspilot.db"
os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.models.membership import Membership


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_context(client):
    payload = {
        "email": "owner@example.com",
        "full_name": "Owner User",
        "password": "VeryStrongPass123!",
        "organization_name": "Acme Field Services",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    token = response.json()["access_token"]

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200

    with SessionLocal() as db:
        membership = db.scalar(select(Membership))
        org_id = str(membership.organization_id)

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": org_id,
    }
    return {"token": token, "org_id": org_id, "headers": headers}
