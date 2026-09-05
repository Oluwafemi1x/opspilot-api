from fastapi import APIRouter, Depends

from app.api.deps import get_membership
from app.models.membership import Membership

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/current")
def current_org(membership: Membership = Depends(get_membership)):
    return {
        "id": membership.organization_id,
        "role": membership.role,
        "name": membership.organization.name,
        "slug": membership.organization.slug,
    }
