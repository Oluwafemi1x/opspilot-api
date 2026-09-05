# OpsPilot API

A production-style, multi-tenant operations management platform built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2**, **JWT authentication**, **role-based access control**, **Alembic migrations**, **pytest**, and a responsive web dashboard served directly by FastAPI.

OpsPilot is designed to demonstrate the engineering patterns expected in real backend systems: secure authentication, tenant isolation, permissions, pagination, filtering, validation, structured errors, automated testing, CI, containerization, and deployment readiness.

## What OpsPilot does

OpsPilot helps organizations manage their operational work in one place.

A company can create an organization workspace, invite team members, manage clients, create and track work orders, control what different users can do, and view operational summary metrics from a modern dashboard.

Each organization is isolated from every other organization, even though they run on the same application and database. This is implemented through tenant-aware queries and membership checks rather than by trusting IDs supplied by the client.

## Core capabilities

- Secure account registration and login
- JWT bearer authentication
- Argon2 password hashing
- Multi-tenant organization workspaces
- Owner / Admin / Member role-based access control
- Client management
- Work-order management
- Priority and status tracking
- Due dates and assignment-ready data model
- Pagination, search and filtering
- Dashboard summary metrics
- Team membership and role management
- Audit logging
- Pydantic validation
- Consistent API error responses
- PostgreSQL persistence
- Alembic database migrations
- Swagger UI and ReDoc
- Responsive browser dashboard
- Docker and Docker Compose
- Render deployment configuration
- GitHub Actions CI
- Automated pytest suite

## Tech stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| Runtime | Python 3.11+ |
| ORM | SQLAlchemy 2 |
| Database | PostgreSQL |
| Validation | Pydantic v2 |
| Authentication | JWT / PyJWT |
| Password security | Argon2 |
| Migrations | Alembic |
| Testing | pytest + HTTPX |
| Frontend | HTML, modern CSS, vanilla JavaScript |
| Containers | Docker / Docker Compose |
| CI | GitHub Actions |
| Deployment | Render-ready configuration |

## Architecture

```text
Browser Dashboard
       |
       v
FastAPI Application
       |
       +-- Authentication / JWT
       +-- Tenant & RBAC dependencies
       +-- API route layer
       +-- Validation schemas
       +-- Audit service
       |
       v
SQLAlchemy 2 ORM
       |
       v
PostgreSQL
```

The application uses a layered structure so HTTP concerns, validation, authorization, persistence and domain operations do not become tightly coupled.

```text
app/
├── api/
│   ├── deps.py
│   ├── router.py
│   └── routes/
├── core/
├── db/
├── models/
├── schemas/
├── services/
├── static/
└── main.py
```

## Multi-tenancy

OpsPilot follows a shared-database, tenant-scoped architecture.

Users belong to organizations through membership records. Tenant-owned resources such as clients and work orders store an `organization_id`. Protected requests resolve the authenticated user's membership before accessing organization data.

A user in Organization A therefore cannot access Organization B's resources simply by guessing an object UUID.

## Authorization model

| Capability | Owner | Admin | Member |
| --- | :---: | :---: | :---: |
| View workspace data | ✅ | ✅ | ✅ |
| Manage clients | ✅ | ✅ | Limited |
| Manage work orders | ✅ | ✅ | Limited |
| View team | ✅ | ✅ | ✅ |
| Change member roles | ✅ | Limited | ❌ |
| Administrative control | ✅ | Limited | ❌ |

Authorization is enforced in backend dependencies and route logic. The browser UI is not treated as a security boundary.

## Authentication flow

1. A user registers or logs in.
2. Passwords are verified using Argon2.
3. The API issues a signed JWT access token.
4. Protected requests send the token as `Authorization: Bearer <token>`.
5. FastAPI resolves the authenticated user.
6. Organization-scoped routes also verify membership and role permissions.

## API areas

The API includes route groups for:

- authentication
- organizations
- team members
- clients
- work orders
- dashboard metrics

Interactive documentation is generated automatically by FastAPI.

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI schema: `/openapi.json`

## Filtering and pagination

Collection endpoints are designed for real application usage rather than returning an unbounded database table.

Supported patterns include:

- page-based pagination
- configurable page size
- text search
- status filtering
- priority filtering
- tenant scoping

Example:

```http
GET /api/v1/organizations/{organization_id}/work-orders?page=1&page_size=20&status=open&priority=high
```

## Dashboard

The browser dashboard is intentionally connected to dedicated API endpoints rather than calculating business totals from whichever page of work orders happens to be loaded.

The dashboard can display operational metrics such as:

- total clients
- total work orders
- open work orders
- completed work orders
- overdue work
- team size

## Web interface

FastAPI also serves a responsive single-page dashboard from the same deployment.

The interface provides:

- registration and sign-in
- workspace-aware navigation
- dashboard metrics
- client creation and browsing
- work-order creation and browsing
- search and filters
- pagination
- team member visibility
- role controls for authorized users
- loading states
- empty states
- validation and server-error feedback
- responsive layouts for desktop and smaller screens

Because the frontend and API ship together, a reviewer can run one service and inspect both the product experience and backend implementation.

## Data model

Primary entities include:

```text
User
  |
  v
Membership >--- Organization
                  |
                  +--- Client
                  |
                  +--- WorkOrder
                  |
                  +--- AuditLog
```

UUID identifiers are used for externally exposed resources.

## Error handling

The API uses structured HTTP exceptions and validation responses instead of leaking raw database or Python errors to clients.

Typical cases include:

- invalid credentials → `401 Unauthorized`
- insufficient permissions → `403 Forbidden`
- missing tenant resource → `404 Not Found`
- invalid request payload → `422 Unprocessable Entity`
- duplicate/conflicting data → appropriate `4xx` response

## Audit logging

Important actions can be recorded with information about the actor, organization, action and affected resource. This pattern provides a foundation for accountability and operational troubleshooting in multi-user systems.

## Database migrations

Schema changes are managed through Alembic.

```bash
alembic upgrade head
```

The repository includes an initial migration for the application schema.

## Local development

### 1. Clone the repository

```bash
git clone https://github.com/Oluwafemi1x/opspilot-api.git
cd opspilot-api
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install the project

```bash
pip install -e ".[dev]"
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and adjust the values.

Important settings include:

```env
DATABASE_URL=postgresql+psycopg://opspilot:opspilot@localhost:5432/opspilot
JWT_SECRET_KEY=replace-this-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Never commit production secrets.

### 5. Start PostgreSQL

The easiest option is Docker Compose:

```bash
docker compose up -d db
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Start the application

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Running with Docker

```bash
docker compose up --build
```

This starts the API and PostgreSQL using the repository's container configuration.

## Testing

Run the automated suite with:

```bash
pytest
```

The suite covers important application flows including authentication, clients, work orders, dashboard data, team membership and frontend delivery.

This project was verified locally with the automated suite passing before publication.

## Continuous integration

The included GitHub Actions workflow installs the project and runs the test suite on pushes and pull requests.

CI is valuable here because authentication and tenant authorization are exactly the types of backend behavior that should be protected from accidental regression.

## Deployment

A `render.yaml` blueprint is included for a PostgreSQL-backed deployment.

A typical production release flow is:

```text
GitHub
  |
  v
CI Tests
  |
  v
Deployment Platform
  |
  +-- FastAPI service
  +-- PostgreSQL database
  +-- environment secrets
  +-- Alembic migration
```

Production secrets must be configured on the hosting platform rather than committed to Git.

## Engineering decisions demonstrated

This repository is intentionally more than a CRUD tutorial. It demonstrates the ability to reason about concerns that appear in real backend work:

- tenant data isolation
- authentication vs. authorization
- secure password storage
- token-based sessions
- database schema design
- relational modeling
- migration management
- query filtering and pagination
- server-side validation
- API error design
- auditability
- automated regression testing
- CI workflows
- containerized development
- deployment configuration
- integrating a frontend with a protected API

## Possible next iterations

Production systems continuously evolve. Logical extensions include:

- refresh-token rotation and token revocation
- email invitations
- password reset flow
- Redis caching
- asynchronous job processing
- rate limiting
- object-level work-order assignments
- WebSocket notifications
- observability with structured metrics/tracing
- expanded integration and load tests

## Author

**Olawumi Oluwafemi (Pycoder)**  
Python Backend Developer — Automation & Debugging

GitHub: https://github.com/Oluwafemi1x  
Portfolio: https://oluwafemi1x.github.io/Task-Manager/  

---

OpsPilot was built as a portfolio-grade backend engineering project focused on secure API design, PostgreSQL data modeling, multi-tenant authorization, automated testing and deployment-ready application structure.
