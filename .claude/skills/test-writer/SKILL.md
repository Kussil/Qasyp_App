---
name: test-writer
description: Write unit and integration tests for Qasyp App following pytest and FastAPI testing conventions. Use when adding tests for a new endpoint, service, Celery task, or RAG component. Target is >70% coverage on all new code.
---

# Test Writer

Generates pytest unit and integration tests for Qasyp App's FastAPI backend. Covers endpoints, services, Celery tasks, and the RAG matching pipeline.

## When to Use

- Writing tests for a new API endpoint
- Writing tests for a new service function
- Testing Celery task behaviour
- Testing the embedding pipeline or match filter logic
- Checking test coverage and identifying gaps

---

## Stack

- **Test runner:** `pytest` with `pytest-asyncio`
- **HTTP test client:** `httpx.AsyncClient` via `asgi-lifespan`
- **Mocking:** `unittest.mock` / `pytest-mock` (`mocker` fixture)
- **Coverage:** `pytest-cov` — target >70% on new code
- **Database:** `SQLAlchemy` async sessions with a test PostgreSQL database (or `pytest-asyncio` with in-memory SQLite for unit tests)
- **Factories:** `factory_boy` for model fixtures

---

## File Structure

```
tests/
  conftest.py               # shared fixtures: app client, db session, auth tokens
  unit/
    services/               # tests for app/services/
    models/                 # tests for app/models/
    tasks/                  # tests for Celery tasks
    agents/                 # tests for agent logic
  integration/
    api/
      v1/
        test_{resource}.py  # tests for app/api/v1/endpoints/
  rag/
    test_embedding.py       # embedding pipeline tests
    test_matching.py        # match query and filter logic tests
```

---

## conftest.py — Shared Fixtures

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.db.base import Base


TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost/qasyp_test"


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac


@pytest.fixture
def auth_headers(client) -> dict:
    """Return valid JWT headers for a test user."""
    # Generate a test token — never use a real secret
    from app.core.security import create_access_token
    token = create_access_token({"sub": "test-user-id", "role": "BUYER"})
    return {"Authorization": f"Bearer {token}"}
```

---

## Endpoint Test Pattern

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_survey_response_success(client: AsyncClient, auth_headers: dict):
    """
    POST /survey/responses should create a new response and return 201.
    """
    payload = {
        "company_name": "Test ТОО",
        "bin": "123456789012",
        "legal_entity_type": "TOO",
        "vat_registered": False,
        "role": "BUYER",
        "industry_sector": "Construction",
        "business_scope": "We procure construction materials for residential projects.",
        "products_services": ["cement", "rebar", "sand"],
        "operating_regions": ["ALMATY_CITY", "ALMATY_REGION"],
        "willing_cross_border": False,
    }

    response = await client.post("/api/v1/survey/responses", json=payload, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["bin"] == "123456789012"
    assert data["role"] == "BUYER"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_survey_response_invalid_bin(client: AsyncClient, auth_headers: dict):
    """
    POST /survey/responses with a BIN that is not 12 digits should return 422.
    """
    payload = {"bin": "123", "company_name": "Test"}
    response = await client.post("/api/v1/survey/responses", json=payload, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_survey_response_unauthenticated(client: AsyncClient):
    """
    POST /survey/responses without an auth token should return 401.
    """
    response = await client.post("/api/v1/survey/responses", json={})
    assert response.status_code == 401
```

---

## Service Test Pattern (with mocking)

```python
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_embed_and_index_profile(mocker):
    """
    embed_and_index_profile should call the embedding model and upsert to vector store.
    Never call the real embedding API in tests.
    """
    mock_embed = mocker.patch(
        "app.services.embedding.embed_text",
        return_value=[0.1] * 1024,
    )
    mock_upsert = mocker.patch(
        "app.services.vector_store.upsert_profile_embedding",
        new_callable=AsyncMock,
    )

    from app.services.matching import embed_and_index_profile
    from tests.factories import BusinessProfileFactory

    profile = BusinessProfileFactory.build()
    await embed_and_index_profile(profile)

    mock_embed.assert_called_once()
    mock_upsert.assert_called_once_with(profile, [0.1] * 1024)
```

---

## Celery Task Test Pattern

```python
import pytest


def test_index_profile_embedding_task_retries_on_failure(mocker):
    """
    index_profile_embedding should retry up to 3 times on exception.
    """
    mocker.patch("app.tasks.embedding.BusinessProfile.get", side_effect=Exception("DB error"))

    from app.tasks.embedding import index_profile_embedding

    with pytest.raises(Exception):
        index_profile_embedding.apply(args=["fake-profile-id"])
```

---

## RAG Match Filter Test Pattern

```python
import pytest
from app.services.matching import build_match_filter
from app.models.profile import Role, Region
from tests.factories import BusinessProfileFactory


def test_buyer_filter_targets_suppliers():
    """Buyer profiles should only match SUPPLIER and BOTH roles."""
    buyer = BusinessProfileFactory.build(
        role=Role.BUYER,
        operating_regions=[Region.ALMATY_CITY],
        willing_cross_border=False,
    )
    f = build_match_filter(buyer, model_version="test-v1")
    role_condition = next(c for c in f.must if c.key == "role")
    assert Role.SUPPLIER.value in role_condition.match.any
    assert Role.BUYER.value not in role_condition.match.any


def test_cross_border_skips_region_filter():
    """Profiles with willing_cross_border=True should not have a region filter."""
    profile = BusinessProfileFactory.build(
        role=Role.BUYER,
        operating_regions=[Region.ALMATY_CITY],
        willing_cross_border=True,
    )
    f = build_match_filter(profile, model_version="test-v1")
    region_keys = [c.key for c in f.must]
    assert "operating_regions" not in region_keys
```

---

## Coverage Check

```bash
# Run all tests with coverage report
pytest --cov=app --cov-report=term-missing --cov-fail-under=70

# Run a specific test file
pytest tests/integration/api/v1/test_survey.py -v

# Run only unit tests
pytest tests/unit/ -v
```

---

## Rules

- Never make real HTTP calls to external APIs (LLM, Qdrant, email) in tests — always mock
- Never use production credentials or real BINs in test fixtures
- All async tests must be decorated with `@pytest.mark.asyncio`
- Use `factory_boy` factories for model fixtures — never build raw dicts by hand
- Test the unhappy path (400, 401, 422, 500) as well as the happy path
- One assertion per logical scenario — split into separate test functions
- Test function names follow: `test_{what}_{condition}` e.g. `test_create_profile_invalid_bin`
