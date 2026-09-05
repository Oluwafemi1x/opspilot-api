from fastapi import APIRouter

from app.api.routes import auth, clients, dashboard, members, organizations, work_orders

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(clients.router)
api_router.include_router(work_orders.router)
api_router.include_router(members.router)
api_router.include_router(dashboard.router)
