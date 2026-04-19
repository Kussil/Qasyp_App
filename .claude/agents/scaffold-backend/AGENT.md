# Scaffold Backend Subagent

> Creates the FastAPI project skeleton with models, config, and Alembic setup.
> Runs inside an isolated worktree. Produces zero business logic — only structure.

---

## Context

Read these files before starting:
- `.claude/skills/api-spec/SKILL.md` — endpoint patterns, Pydantic conventions
- `.claude/skills/alembic-migration/SKILL.md` — migration setup patterns
- `.claude/context/profile-schema.md` — canonical data model (defines all DB models)
- `.claude/CLAUDE.md` §5 — technical stack reference

---

## Working Directory

You are running inside a worktree. All file operations MUST use the worktree path:
```
.claude/worktrees/scaffold-backend/
```

**Never** modify files in the repository root. Work only within your worktree.

---

## What to Create

### Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app factory, CORS, lifespan
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Pydantic BaseSettings (env vars)
│   │   ├── security.py           # JWT creation, password hashing (bcrypt)
│   │   └── database.py           # async SQLAlchemy engine + session factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py               # DeclarativeBase with common columns (id, created_at, updated_at)
│   │   ├── user.py               # User model (email, hashed_password, role, tier)
│   │   └── profile.py            # BusinessProfile model (ALL fields from profile-schema.md)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py               # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── user.py               # UserResponse, UserUpdate
│   │   ├── profile.py            # ProfileCreate, ProfileResponse (from profile-schema.md)
│   │   └── match.py              # MatchResult, MatchListResponse
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py         # APIRouter aggregating all endpoint routers
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── health.py     # GET /health → {"status": "ok"}
│   ├── services/
│   │   └── __init__.py           # Empty — feature subagents add service modules
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── celery_app.py         # Celery app configuration
│   └── agents/
│       └── __init__.py           # Empty — E5 subagent adds agent modules
├── alembic/
│   ├── env.py                    # Async Alembic env (from alembic-migration skill)
│   ├── script.py.mako
│   └── versions/
│       └── .gitkeep
├── alembic.ini
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Async fixtures (from test-writer skill)
│   ├── unit/
│   │   └── __init__.py
│   ├── integration/
│   │   └── __init__.py
│   └── rag/
│       └── __init__.py
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── pyproject.toml                # ruff + pytest config
└── .env.example
```

### Key File Contents

**app/main.py** — FastAPI application factory:
- `create_app()` function returning FastAPI instance
- CORS middleware (allow all origins in dev, restrict in production via env var)
- Lifespan context manager for startup/shutdown (DB engine disposal)
- Include v1 router at prefix `/api/v1`
- Health endpoint at `/health`

**app/core/config.py** — Settings via Pydantic BaseSettings:
- `DATABASE_URL` (PostgreSQL async URL)
- `REDIS_URL`
- `QDRANT_URL` and `QDRANT_COLLECTION`
- `SECRET_KEY` and `JWT_ALGORITHM` (HS256) and `ACCESS_TOKEN_EXPIRE_MINUTES` (30) and `REFRESH_TOKEN_EXPIRE_DAYS` (7)
- `ANTHROPIC_API_KEY`
- `EMBEDDING_MODEL_VERSION` (default: `multilingual-e5-large`)
- `ENVIRONMENT` (dev/staging/production)
- `DEMO_MODE` (bool, default: False)
- Load from `.env` file

**app/core/database.py** — Async SQLAlchemy:
- `create_async_engine` with `DATABASE_URL`
- `async_sessionmaker` with `expire_on_commit=False`
- `get_db()` async generator dependency

**app/core/security.py** — Stubs:
- `hash_password(plain: str) -> str` using bcrypt
- `verify_password(plain: str, hashed: str) -> bool`
- `create_access_token(data: dict) -> str`
- `create_refresh_token(data: dict) -> str`
- `decode_token(token: str) -> dict`

**app/models/base.py** — Base model:
- `id: Mapped[uuid.UUID]` primary key with `default_factory=uuid4`
- `created_at: Mapped[datetime]` with `server_default=func.now()`
- `updated_at: Mapped[datetime]` with `onupdate=func.now()`

**app/models/user.py** — User:
- `email: Mapped[str]` unique, indexed
- `hashed_password: Mapped[str]`
- `role: Mapped[Optional[str]]` — BUYER / SUPPLIER / null
- `tier: Mapped[str]` — free / basic / pro (default: free)
- `is_active: Mapped[bool]` (default: True)
- Relationship to `BusinessProfile` (one-to-one)

**app/models/profile.py** — BusinessProfile:
- Map EVERY field from `.claude/context/profile-schema.md`
- `user_id: Mapped[uuid.UUID]` foreign key to users.id
- `embedding_generated: Mapped[bool]` (default: False)
- `demo: Mapped[bool]` (default: False) — for seed data tagging

**Pydantic schemas** — Follow api-spec skill patterns:
- Base → Create → Response pattern
- `model_config = ConfigDict(from_attributes=True)`
- Enum classes for: `LegalEntityType`, `Role`, `Tier`, `Frequency`, `RevenueRange`, `Region`

**requirements.txt:**
```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
sqlalchemy[asyncio]>=2.0.30
asyncpg>=0.29.0
alembic>=1.13.0
pydantic>=2.7.0
pydantic-settings>=2.2.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
celery[redis]>=5.4.0
redis>=5.0.0
qdrant-client>=1.9.0
httpx>=0.27.0
python-dotenv>=1.0.0
anthropic>=0.25.0
```

**requirements-dev.txt:**
```
pytest>=8.2.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0
httpx>=0.27.0
factory-boy>=3.3.0
ruff>=0.4.0
mypy>=1.10.0
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**.env.example:** — All env vars from config.py with placeholder values

**pyproject.toml:** — ruff config (line-length=100, target=py311) + pytest config (asyncio_mode=auto)

---

## Commit

When done, commit all files:
```bash
git add -A
git commit -m "feat(scaffold): add FastAPI backend skeleton with models, config, and Alembic

- App factory with CORS and lifespan
- User and BusinessProfile models (from profile-schema.md)
- Pydantic v2 schemas with enums
- Async SQLAlchemy + Alembic setup
- JWT security stubs (bcrypt + python-jose)
- Celery app configuration
- Test directory with async conftest
- Dockerfile and requirements

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Output Checklist

- [ ] All directories and `__init__.py` files created
- [ ] `profile.py` model has ALL fields from profile-schema.md
- [ ] Enums match profile-schema.md values exactly
- [ ] Config loads all required env vars
- [ ] Health endpoint works: `GET /health` → 200
- [ ] No hardcoded secrets anywhere
- [ ] `.env.example` lists every env var
- [ ] `ruff check .` passes with zero errors
- [ ] Committed with Conventional Commit format
