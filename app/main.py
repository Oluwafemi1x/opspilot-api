from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    summary="Multi-tenant service operations backend",
    description=(
        "A production-style FastAPI backend demonstrating JWT authentication, "
        "role-based permissions, tenant isolation, PostgreSQL, Alembic migrations, "
        "validation, pagination/filtering, audit logs, tests and containerized deployment."
    ),
    contact={
        "name": "Olawumi Oluwafemi (Pycoder)",
        "url": "https://github.com/Oluwafemi1x",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/app", StaticFiles(directory=STATIC_DIR), name="app")


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "service": "opspilot-api",
        "environment": settings.app_env,
    }


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(_: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database operation failed", "code": "database_error"},
    )
