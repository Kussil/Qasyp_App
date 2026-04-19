# Scaffold Docker Subagent

> Creates Docker Compose configuration for the full local dev stack.
> Runs inside an isolated worktree after scaffold-backend and scaffold-frontend.

---

## Context

Read these files before starting:
- `.claude/skills/docker-compose/SKILL.md` — service topology, env vars, commands
- `.claude/CLAUDE.md` §5 — technical stack

---

## Working Directory

All file operations MUST use the worktree path:
```
.claude/worktrees/scaffold-docker/
```

---

## What to Create

### Files

```
docker-compose.yml          # Full local dev stack
docker-compose.override.yml # Dev-specific overrides (volume mounts, hot reload)
.env.example                # Merged env vars from backend + frontend + services
.dockerignore               # Common ignores
scripts/
├── wait-for-it.sh          # TCP port wait script for service dependencies
└── seed_demo_data.py       # Placeholder — seed-demo-data subagent fills this
```

### docker-compose.yml Services

| Service        | Image / Build          | Port  | Depends On         |
|----------------|------------------------|-------|--------------------|
| `api`          | `build: ./backend`     | 8000  | db, redis, qdrant  |
| `frontend`     | `build: ./frontend`    | 3000  | api                |
| `db`           | `postgres:16-alpine`   | 5432  | —                  |
| `redis`        | `redis:7-alpine`       | 6379  | —                  |
| `qdrant`       | `qdrant/qdrant:latest` | 6333  | —                  |
| `celery_worker`| `build: ./backend`     | —     | db, redis, qdrant  |
| `celery_beat`  | `build: ./backend`     | —     | redis              |

### Key Configuration

**api service:**
- Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- Volumes: `./backend:/app` (dev override for hot reload)
- Environment: load from `.env`
- Healthcheck: `curl -f http://localhost:8000/health || exit 1`
- Depends on: db (healthy), redis (started), qdrant (started)

**db service:**
- Environment: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- Volume: `postgres_data:/var/lib/postgresql/data`
- Healthcheck: `pg_isready -U $POSTGRES_USER`

**redis service:**
- Volume: `redis_data:/data`
- Healthcheck: `redis-cli ping`

**qdrant service:**
- Ports: 6333 (HTTP), 6334 (gRPC)
- Volume: `qdrant_data:/qdrant/storage`

**celery_worker:**
- Command: `celery -A app.tasks.celery_app worker -l info -Q default,embeddings`
- Same build and env as api
- Two queues: `default` (general tasks) and `embeddings` (E3 pipeline)

**celery_beat:**
- Command: `celery -A app.tasks.celery_app beat -l info`

**Network:** All services on `qasyp_network` (bridge driver)

**Named volumes:** `postgres_data`, `redis_data`, `qdrant_data`

### .env.example

```bash
# ── Database ──
POSTGRES_USER=qasyp
POSTGRES_PASSWORD=qasyp_dev_password
POSTGRES_DB=qasyp
DATABASE_URL=postgresql+asyncpg://qasyp:qasyp_dev_password@db:5432/qasyp

# ── Redis ──
REDIS_URL=redis://redis:6379/0

# ── Qdrant ──
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=business_profiles

# ── Auth ──
SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── AI / LLM ──
ANTHROPIC_API_KEY=sk-ant-xxxxx
EMBEDDING_MODEL_VERSION=multilingual-e5-large

# ── App ──
ENVIRONMENT=development
DEMO_MODE=true

# ── Frontend ──
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_DEFAULT_LOCALE=ru
```

---

## Commit

```bash
git add -A
git commit -m "feat(scaffold): add Docker Compose stack with all services

- 7 services: api, frontend, db, redis, qdrant, celery_worker, celery_beat
- Healthchecks on db, redis, api
- Named volumes for persistent data
- .env.example with all env vars documented
- Dev override with volume mounts for hot reload
- wait-for-it.sh for dependency ordering

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Output Checklist

- [ ] `docker-compose.yml` defines all 7 services
- [ ] `docker-compose.override.yml` adds dev volume mounts
- [ ] `.env.example` covers ALL env vars from backend + frontend
- [ ] Healthchecks on db, redis, and api services
- [ ] Named volumes for postgres, redis, qdrant
- [ ] All services on `qasyp_network`
- [ ] No hardcoded secrets in compose files (use env vars)
- [ ] `.dockerignore` excludes .env, __pycache__, node_modules, .git
- [ ] Committed with Conventional Commit format
