from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_membership
from app.db.session import get_db
from app.models.client import Client
from app.models.membership import Membership
from app.models.work_order import Priority, WorkOrder, WorkOrderStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_membership),
):
    org_id = membership.organization_id

    total_clients = db.scalar(
        select(func.count()).select_from(Client).where(Client.organization_id == org_id)
    ) or 0

    status_rows = db.execute(
        select(WorkOrder.status, func.count(WorkOrder.id))
        .where(WorkOrder.organization_id == org_id)
        .group_by(WorkOrder.status)
    ).all()

    status_counts = {status.value: count for status, count in status_rows}
    total_work = sum(status_counts.values())
    completed = status_counts.get(WorkOrderStatus.completed.value, 0)
    open_work = sum(
        count
        for work_status, count in status_counts.items()
        if work_status
        not in {WorkOrderStatus.completed.value, WorkOrderStatus.cancelled.value}
    )

    high_priority = db.scalar(
        select(func.count())
        .select_from(WorkOrder)
        .where(
            WorkOrder.organization_id == org_id,
            WorkOrder.priority.in_([Priority.high, Priority.urgent]),
            WorkOrder.status.notin_([WorkOrderStatus.completed, WorkOrderStatus.cancelled]),
        )
    ) or 0

    return {
        "clients": total_clients,
        "work_orders": total_work,
        "open_work": open_work,
        "high_priority": high_priority,
        "completed": completed,
        "completion_rate": round((completed / total_work) * 100) if total_work else 0,
        "by_status": {
            work_status.value: status_counts.get(work_status.value, 0)
            for work_status in WorkOrderStatus
        },
    }
