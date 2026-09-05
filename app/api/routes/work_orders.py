import math
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_membership, require_roles
from app.db.session import get_db
from app.models.client import Client
from app.models.membership import Membership, Role
from app.models.user import User
from app.models.work_order import Priority, WorkOrder, WorkOrderStatus
from app.schemas.common import Page
from app.schemas.work_order import WorkOrderCreate, WorkOrderResponse, WorkOrderUpdate
from app.services.audit import record_audit

router = APIRouter(prefix="/work-orders", tags=["Work Orders"])


def validate_client(db: Session, org_id: uuid.UUID, client_id: uuid.UUID | None):
    if client_id and not db.scalar(
        select(Client.id).where(
            Client.id == client_id,
            Client.organization_id == org_id,
        )
    ):
        raise HTTPException(422, "client_id does not belong to this organization")


@router.post("", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
def create_work_order(
    payload: WorkOrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    membership: Membership = Depends(get_membership),
):
    validate_client(db, membership.organization_id, payload.client_id)
    item = WorkOrder(
        organization_id=membership.organization_id,
        created_by_id=user.id,
        **payload.model_dump(),
    )
    db.add(item)
    db.flush()
    record_audit(
        db,
        membership.organization_id,
        user.id,
        "work_order.created",
        "work_order",
        item.id,
        {"priority": item.priority.value},
    )
    db.commit()
    db.refresh(item)
    return item


@router.get("", response_model=Page[WorkOrderResponse])
def list_work_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: WorkOrderStatus | None = Query(None, alias="status"),
    priority: Priority | None = None,
    assigned_to_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
    due_before: datetime | None = None,
    search: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_membership),
):
    filters = [WorkOrder.organization_id == membership.organization_id]
    if status_filter:
        filters.append(WorkOrder.status == status_filter)
    if priority:
        filters.append(WorkOrder.priority == priority)
    if assigned_to_id:
        filters.append(WorkOrder.assigned_to_id == assigned_to_id)
    if client_id:
        filters.append(WorkOrder.client_id == client_id)
    if due_before:
        filters.append(WorkOrder.due_at <= due_before)
    if search:
        q = f"%{search.strip()}%"
        filters.append(or_(WorkOrder.title.ilike(q), WorkOrder.description.ilike(q)))

    total = db.scalar(select(func.count()).select_from(WorkOrder).where(*filters)) or 0
    items = db.scalars(
        select(WorkOrder)
        .where(*filters)
        .order_by(WorkOrder.created_at.desc())
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


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order(
    work_order_id: uuid.UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_membership),
):
    item = db.scalar(
        select(WorkOrder).where(
            WorkOrder.id == work_order_id,
            WorkOrder.organization_id == membership.organization_id,
        )
    )
    if not item:
        raise HTTPException(404, "Work order not found")
    return item


@router.patch("/{work_order_id}", response_model=WorkOrderResponse)
def update_work_order(
    work_order_id: uuid.UUID,
    payload: WorkOrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    membership: Membership = Depends(get_membership),
):
    item = db.scalar(
        select(WorkOrder).where(
            WorkOrder.id == work_order_id,
            WorkOrder.organization_id == membership.organization_id,
        )
    )
    if not item:
        raise HTTPException(404, "Work order not found")

    data = payload.model_dump(exclude_unset=True)
    validate_client(db, membership.organization_id, data.get("client_id"))
    for key, value in data.items():
        setattr(item, key, value)

    record_audit(
        db,
        membership.organization_id,
        user.id,
        "work_order.updated",
        "work_order",
        item.id,
        {"changed": sorted(data.keys())},
    )
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{work_order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_order(
    work_order_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_roles(Role.owner, Role.admin)),
):
    item = db.scalar(
        select(WorkOrder).where(
            WorkOrder.id == work_order_id,
            WorkOrder.organization_id == membership.organization_id,
        )
    )
    if not item:
        raise HTTPException(404, "Work order not found")

    record_audit(
        db,
        membership.organization_id,
        user.id,
        "work_order.deleted",
        "work_order",
        item.id,
    )
    db.delete(item)
    db.commit()
    return Response(status_code=204)
