import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_membership, require_roles
from app.db.session import get_db
from app.models.membership import Membership, Role
from app.schemas.member import MemberResponse, MemberRoleUpdate

router = APIRouter(prefix="/members", tags=["Team Members"])


@router.get("", response_model=list[MemberResponse])
def list_members(
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_membership),
):
    rows = db.scalars(
        select(Membership)
        .options(joinedload(Membership.user))
        .where(Membership.organization_id == membership.organization_id)
        .order_by(Membership.created_at.asc())
    ).all()

    return [
        MemberResponse(
            membership_id=row.id,
            user_id=row.user_id,
            full_name=row.user.full_name,
            email=row.user.email,
            role=row.role,
            is_active=row.user.is_active,
        )
        for row in rows
    ]


@router.patch("/{membership_id}", response_model=MemberResponse)
def update_member_role(
    membership_id: uuid.UUID,
    payload: MemberRoleUpdate,
    db: Session = Depends(get_db),
    actor: Membership = Depends(require_roles(Role.owner)),
):
    target = db.scalar(
        select(Membership)
        .options(joinedload(Membership.user))
        .where(
            Membership.id == membership_id,
            Membership.organization_id == actor.organization_id,
        )
    )
    if not target:
        raise HTTPException(404, "Member not found")
    if target.id == actor.id and payload.role != Role.owner:
        raise HTTPException(422, "The active owner cannot downgrade their own role")

    target.role = payload.role
    db.commit()
    db.refresh(target)

    return MemberResponse(
        membership_id=target.id,
        user_id=target.user_id,
        full_name=target.user.full_name,
        email=target.user.email,
        role=target.role,
        is_active=target.user.is_active,
    )
