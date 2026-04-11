# Skill: api-spec

## Purpose
Generate FastAPI endpoint stubs, Pydantic models, and OpenAPI-compliant code that conform to Qasyp App's backend conventions without requiring repeated context.

## When to Use
Invoke this skill whenever you are:
- Creating a new API endpoint (route, schema, service layer)
- Writing Pydantic models for request/response bodies
- Generating database migration stubs (Alembic)
- Writing unit or integration test skeletons for API routes

---

## Project Stack Context
- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy (async) with PostgreSQL
- **Auth:** JWT Bearer tokens; OAuth2PasswordBearer
- **Validation:** Pydantic v2
- **Task Queue:** Celery + Redis
- **LLM Calls:** Always wrapped in try/except with token usage logging
- **Migrations:** Alembic

---

## Code Conventions

### General
- PEP 8 strictly enforced
- All docstrings and code comments in **English**
- UI-facing strings go in i18n files, never hardcoded
- Never hardcode secrets — use environment variables via `python-dotenv`
- Conventional Commits format: `feat(E2): add adaptive survey branching logic`

### File Structure
```
app/
  api/
    v1/
      endpoints/      # Route handlers only — no business logic
      schemas/        # Pydantic request/response models
  services/           # Business logic layer
  models/             # SQLAlchemy ORM models
  core/
    config.py         # Settings (pydantic BaseSettings)
    security.py       # JWT helpers
  tasks/              # Celery tasks
  agents/             # LangGraph / CrewAI agent definitions
```

### Endpoint Pattern
```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.schemas.{resource} import {Resource}Create, {Resource}Response
from app.services.{resource} import {resource}_service

router = APIRouter(prefix="/{resources}", tags=["{Resources}"])

@router.post("/", response_model={Resource}Response, status_code=status.HTTP_201_CREATED)
async def create_{resource}(
    payload: {Resource}Create,
    current_user: User = Depends(get_current_user),
) -> {Resource}Response:
    """
    Create a new {resource}.
    Requires authenticated user.
    """
    return await {resource}_service.create(payload, owner_id=current_user.id)
```

### Pydantic Schema Pattern
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class {Resource}Base(BaseModel):
    # shared fields

class {Resource}Create({Resource}Base):
    # input-only fields

class {Resource}Response({Resource}Base):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
```

### LLM Call Pattern (mandatory)
```python
import logging
logger = logging.getLogger(__name__)

async def call_llm(prompt: str) -> str:
    try:
        response = await llm_client.generate(prompt)
        logger.info("LLM call succeeded", extra={"tokens": response.usage.total_tokens})
        return response.content
    except Exception as e:
        logger.error("LLM call failed: %s", str(e))
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
```

---

## Epic ID Reference (use in commit messages and tags)
| ID  | Epic                   |
|-----|------------------------|
| E1  | User Onboarding & Auth |
| E2  | Survey Engine          |
| E3  | Matching Engine (RAG)  |
| E4  | Freemium & Paywall     |
| E5  | AI Agent Outreach      |
| E6  | User Dashboard         |
| E7  | Admin & Analytics      |

---

## Output Checklist
Before finalising any generated code, verify:
- [ ] No hardcoded secrets or connection strings
- [ ] LLM calls wrapped in try/except with logging
- [ ] Pydantic models use `from_attributes = True` for ORM compat
- [ ] Route returns correct HTTP status code
- [ ] Docstring present on every public function
- [ ] Commit message follows Conventional Commits with Epic ID
