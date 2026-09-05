import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_membership, require_roles
from app.db.session import get_db
from app.models.client import Client
from app.models.membership import Membership, Role
from app.models.user import User
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate
from app.schemas.common import Page
from app.services.audit import record_audit

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_roles(Role.owner, Role.admin)),
):
    client = Client(
        organization_id=membership.organization_id,
        **payload.model_dump(),
    )
    db.add(client)
    db.flush()
    record_audit(
        db,
        membership.organization_id,
        user.id,
        "client.created",
        "client",
        client.id,
    )
    db.commit()
    db.refresh(client)
    return client


@router.get("", response_model=Page[ClientResponse])
def list_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, min_length=1, max_length=100),
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_membership),
):
    filters = [Client.organization_id == membership.organization_id]
    if search:
        q = f"%{search.strip()}%"
        filters.append(or_(Client.name.ilike(q), Client.email.ilike(q)))

    total = db.scalar(select(func.count()).select_from(Client).where(*filters)) or 0
    items = db.scalars(
        select(Client)
        .where(*filters)
        .order_by(Client.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return Page(
        items=list(items),
        page=page,
        page_size=page_size,
        total=total,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_membership),
):
    client = db.scalar(
        select(Client).where(
            Client.id == client_id,
            Client.organization_id == membership.organization_id,
        )
    )
    if not client:
        raise HTTPException(404, "Client not found")
    return client


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: uuid.UUID,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_roles(Role.owner, Role.admin)),
):
    client = db.scalar(
        select(Client).where(
            Client.id == client_id,
            Client.organization_id == membership.organization_id,
        )
    )
    if not client:
        raise HTTPException(404, "Client not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(client, key, value)

    record_audit(
        db,
        membership.organization_id,
        user.id,
        "client.updated",
        "client",
        client.id,
    )
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_roles(Role.owner)),
):
    client = db.scalar(
        select(Client).where(
            Client.id == client_id,
            Client.organization_id == membership.organization_id,
        )
    )
    if not client:
        raise HTTPException(404, "Client not found")

    record_audit(
        db,
        membership.organization_id,
        user.id,
        "client.deleted",
        "client",
        client.id,
    )
    db.delete(client)
    db.commit()
    return Response(status_code=204)
