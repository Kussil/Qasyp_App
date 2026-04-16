# Demo MVP Build Report
**Branch:** `demo/mvp`
**Date:** 2026-04-16
**Orchestrator:** MVP Orchestrator Agent

---

## Summary

The Demo MVP was built across 3 phases using 9 isolated git worktrees. The result is a stakeholder-ready demo journey: **Register → Survey → Match → Results → Paywall gate**.

---

## Phase 1 — Scaffold (sequential)

| Subagent | Status | Commit | Files Created |
|---|---|---|---|
| scaffold-backend | ✅ Success | `107f238` | 38 files — FastAPI skeleton, models, Alembic, schemas, Celery |
| scaffold-frontend | ✅ Success | `e92fcce` | 43 files — Next.js 14 App Router, Tailwind, i18n (kk/ru/en), UI primitives |
| scaffold-docker | ✅ Success | `5639631` | 6 files — Docker Compose (7 services), .env.example, wait-for-it.sh |

---

## Phase 2 — Build Features (parallel worktrees, sequential merge)

| Subagent | Epic | Status | Commit | Key Deliverables |
|---|---|---|---|---|
| build-e1-auth | E1 | ✅ Success | `5b5b909` | POST /auth/register, /auth/login, /auth/refresh, PATCH /users/me/role, get_current_user dep |
| build-e2-survey | E2 | ✅ Success | `ab71616` | GET /survey/questions, POST /survey/submit, survey_config.json (4 sections, all fields) |
| build-e3-matching | E3 | ✅ Success | `a9bce33` | Embedding service (multilingual-e5-large), Qdrant upsert, hard filters, GET /matches, LLM explanations |
| seed-demo-data | — | ✅ Success | `64ce587` | 20 demo profiles (10 buyer + 10 supplier, 5 industries, 8+ regions) |
| build-e4-paywall-demo | E4 | ✅ Success | `f38d5f4` | POST /demo/upgrade (DEMO_MODE guard), LockedMatchCard, UnlockBanner, DemoModeBanner |
| build-e6-dashboard | E6 | ✅ Success | `055682b` + `2582407` | MatchCard, MatchScoreBadge, DashboardHeader, MatchResultsList, EmptyState, LoadingState, useMatches hook |

### Merge Conflicts Resolved

| File | Resolution |
|---|---|
| `backend/app/api/v1/router.py` | Combined all routers (E1 + E2 + E3 + E4) into final import list |
| `backend/app/api/deps.py` | Kept E1 full JWT implementation (over E2 stub) |
| `backend/app/tasks/embedding_tasks.py` | Kept E3 full Celery implementation (over E2 stub) |

---

## Phase 3 — Verification

| Check | Result |
|---|---|
| Python syntax (all `.py` files) | ✅ Pass — 0 errors |
| No hardcoded secrets | ✅ Pass — no `sk-ant-` or raw `SECRET_KEY=` in code |
| Router wiring | ✅ Pass — all 6 routers imported and registered |
| Embedding task registered | ✅ Pass — `generate_embedding` present in tasks |
| Hard filter logic present | ✅ Pass — `build_qdrant_filter` in matching_service |
| Expected file structure | ✅ Pass — 56 backend .py files, 45 frontend .ts/.tsx files |
| Docker Compose | ✅ Present — 7-service stack (api, frontend, db, redis, qdrant, celery_worker, celery_beat) |

> **Note:** Full `pytest` run and `docker compose up` boot not executed (requires Python/Node deps and Docker daemon). These are the next manual verification steps.

---

## Architectural Decisions Made for Demo

| ADR | Demo Default | Rationale |
|---|---|---|
| ADR-001 (Payment) | Mock upgrade via `POST /demo/upgrade` | No real payment; DEMO_MODE flag ensures 404 in production |
| ADR-002 (Data Residency) | Local Docker (no cloud) | All services run on localhost via Docker Compose |
| ADR-003 (Embedding Model) | `multilingual-e5-large` via sentence-transformers | Best Kazakh+Russian coverage; explicitly labeled in code |

All demo defaults are clearly marked in code via `DEMO_MODE` config flag and comments.

---

## Files Created by Epic

| Epic | Backend Files | Frontend Files |
|---|---|---|
| Scaffold | 38 backend files | 43 frontend files |
| E1 Auth | 7 new files (deps, auth/users endpoints, auth_service, 3 test files) | — |
| E2 Survey | 5 new files (survey endpoint, survey_service, embedding_tasks stub, config JSON, 2 test files) | — |
| E3 Matching | 9 new files (embedding/matching/explanation services, Celery task, matches endpoint, 4 test files) | — |
| E4 Paywall | 4 new backend files (demo endpoint, tier_service, 2 test files) | 4 frontend components (LockedMatchCard, UnlockBanner, DemoModeBanner, index.ts) |
| E6 Dashboard | — | 7 new frontend components (MatchCard, MatchScoreBadge, DashboardHeader, MatchResultsList, EmptyState, LoadingState) + useMatches hook + lib/matches.ts |
| Seed Data | 4 files (demo_profiles.json, seed_demo_data.py, scripts/__init__.py, test_seed_data.py) | — |

---

## Known Limitations / Next Steps

1. **Run `pytest`** — integration tests require a live PostgreSQL instance; unit tests should pass standalone
2. **Run `docker compose up`** to verify full stack boot and API health endpoint
3. **Run seed script** after stack is up: `docker compose exec api python scripts/seed_demo_data.py`
4. **Run Alembic migrations**: `docker compose exec api alembic upgrade head`
5. **E2 survey frontend** — survey wizard components (SurveyWizard, QuestionField, etc.) not implemented (E2 scope was backend-only in this sprint)
6. **E1 auth frontend** — login/register forms are page shells; form logic deferred
7. **Sentence-transformers** — model download on first run (~1 GB); ensure internet access or pre-cache in Docker image
8. **ADR-001/002/003** remain unresolved for production — demo defaults must be replaced before go-live

---

## Demo Journey

```
1. Register:   POST /api/v1/auth/register
2. Set role:   PATCH /api/v1/users/me/role  {"role": "buyer"}
3. Survey:     POST /api/v1/survey/submit   (full profile payload)
4. Match:      GET  /api/v1/matches         (free: top 5 + locked cards)
5. Upgrade:    POST /api/v1/demo/upgrade    (DEMO_MODE=true only)
6. Full list:  GET  /api/v1/matches         (now returns all results)
```
