# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project State

Greenfield — no application code exists yet. The repo currently contains planning artifacts only:
- `.claude/CLAUDE.md` — full product spec, epics, quality attributes, and AI assistant conventions
- `.claude/context/profile-schema.md` — canonical business profile data model (source of truth for E2/E3/E5)
- `.claude/agents/` — agent prompt definitions (sprint-prep, outreach-draft)
- `docs/` — Architecture Decision Records (ADR-001 payment, ADR-002 data residency, ADR-003 embeddings) — all `PROPOSED`, none resolved
- `sprints/` — sprint briefs (none yet); `research/` — market research (none yet)
- `agent-logs/` — audit trail for E5 agent outreach (append-only JSON logs)

---

## Planned Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python) |
| AI / LLM | LangChain or LlamaIndex + Anthropic Claude API |
| Vector DB | Qdrant or pgvector |
| Relational DB | PostgreSQL |
| Task Queue | Celery + Redis |
| Agent Orchestration | LangGraph or CrewAI |
| Frontend | Next.js (TypeScript) |
| Auth | JWT + OAuth2 |
| Containerisation | Docker + Docker Compose (dev) |
| CI/CD | GitHub Actions |

---

## Development Commands

No application code exists yet. When services are scaffolded, expected commands are:

```bash
# Start local stack
docker compose up

# Backend (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Run all tests
pytest

# Run a single test file
pytest tests/path/to/test_file.py -v

# Run a single test
pytest tests/path/to/test_file.py::test_function_name -v

# Frontend (Next.js)
cd frontend
npm install
npm run dev

# Lint (Python)
ruff check .

# Lint (TypeScript)
npm run lint
```

---

## Architecture

### Data flow

```
Survey Engine (E2) → Profile Store (PostgreSQL)
                   → Embedding Pipeline → Vector DB (Qdrant/pgvector)
                                        → RAG Matching Engine (E3)
                                                    ↓
                                   Free shortlist (top 3–5) | Full list (paid)
                                                                     ↓
                                                    AI Agent Orchestrator (E5)
                                                                     ↓
                                              Outreach draft → human approval → send
```

### Epics

| ID | Name | Status |
|---|---|---|
| E1 | User Onboarding & Auth | Not started |
| E2 | Survey Engine | Not started |
| E3 | Matching Engine (RAG) | Not started |
| E4 | Freemium & Paywall | Not started (blocked: ADR-001) |
| E5 | AI Agent Outreach | Not started |
| E6 | User Dashboard | Not started |
| E7 | Admin & Analytics | Not started |

### Embedding strategy

Fields concatenated for vector embedding: `business_scope`, `products_services`, `industry_sector`, `quality_standards`, `preferred_partner_profile`, `growth_target`.

Hard-filter fields (not embedded, applied before vector search): `role` (Buyer ↔ Supplier must be complementary), `operating_regions` (must overlap unless `willing_cross_border=true`), `annual_revenue_range`.

Every embedding record must carry an `embedding_model_version` metadata tag — a model change requires full re-indexing.

---

## Key Conventions

- **Branching:** `feature/[epic-id]-[short-description]` (e.g. `feature/e2-survey-branching`)
- **Commits:** Conventional Commits with Epic ID scope — `feat(E2): add adaptive survey branching logic`
- **Language:** Code comments and docstrings in English; UI copy in Kazakh/Russian via i18n files
- **LLM calls:** Wrap in try/except with fallback; log token usage per request
- **Agent actions:** No agent takes irreversible external actions (e.g. send email) without `approved_by_user: true` — mandatory human-in-the-loop gate, especially in staging
- **Agent logs:** `agent-logs/` entries are append-only — never delete or modify
- **Test coverage target:** >70% on all new code

## Open Architectural Decisions (blocking work)

- **ADR-001** — Payment gateway (E4 blocked): Kaspi Pay vs Halyk Bank vs Stripe — pending commercial/legal review
- **ADR-002** — Data residency (affects all epics): Kazteleport vs AWS Frankfurt vs hybrid — pending legal review of KZ data localisation law
- **ADR-003** — Embedding model (E3 blocked): multilingual-e5-large vs OpenAI vs Cohere — pending benchmark on KZ business profiles; Kazakh language coverage is the critical variable

---

## Available Claude Agents & Skills

**Agents** (run via `.claude/agents/`):
- `sprint-prep` — generates a sprint planning brief in `sprints/sprint-{N}-brief.md`
- `outreach-draft` — drafts E5 outreach messages with audit log entry

**Skills** (invoke with `/skill-name`):
- `/survey-flow` — design/validate E2 survey question flows
- `/rag-pipeline` — write/review E3 embedding and retrieval code
- `/api-spec` — generate API specs
- `/alembic-migration` — generate database migrations
- `/docker-compose` — maintain local dev Docker Compose config
- `/test-writer` — write pytest/FastAPI tests
- `/conventional-commit` — draft/validate commit messages
- `/github-pr` — manage PR lifecycle
- `/code-review` — review code against project standards

---

## AI Assistant Behavioral Guidelines

Behavioral guidelines to reduce common LLM coding mistakes.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
