---
name: code-review
description: Review code against Qasyp App's quality standards before merge. Use when a pull request is ready for review, or when checking any new code for correctness, security, and consistency with project conventions.
---

# Code Review

Structured code review for Qasyp App following PEP 8, OWASP Top 10, FastAPI conventions, and the project's Definition of Done.

## When to Use

- A pull request is ready to be reviewed before merging into `develop`
- A developer wants a pre-review pass on their own code before opening a PR
- Checking a file for issues after a major change

---

## Review Process

### Step 1 — Read the diff

```bash
git diff origin/develop...HEAD
```

Read every changed file. Do not skim. Note the epic the change belongs to.

### Step 2 — Run automated checks

```bash
# Linting
ruff check app/

# Type checking
mypy app/

# Tests
pytest --cov=app --cov-report=term-missing

# Secret scanning
grep -rn "password\s*=\s*['\"]" app/
grep -rn "secret\s*=\s*['\"]" app/
grep -rn "api_key\s*=\s*['\"]" app/
```

### Step 3 — Apply the review checklist below

---

## Review Checklist

### Security
- [ ] No hardcoded secrets, passwords, API keys, or connection strings
- [ ] All environment-dependent values use `os.getenv()` or `settings` from `core/config.py`
- [ ] JWT handling follows the pattern in `core/security.py`
- [ ] User input is validated via Pydantic before use — never used raw
- [ ] SQL queries use ORM or parameterised queries — no string interpolation
- [ ] File uploads (if any) are validated for type and size
- [ ] OWASP Top 10 considered for any authentication, authorisation, or data exposure changes

### Code Quality
- [ ] PEP 8 compliant (enforced by `ruff`)
- [ ] Type annotations present on all function signatures
- [ ] All public functions and classes have docstrings in English
- [ ] No commented-out code left in
- [ ] No `print()` statements — use `logging` instead
- [ ] No `TODO` comments without a linked issue or story

### Architecture
- [ ] Route handlers contain no business logic — logic is in `services/`
- [ ] No direct database access from `endpoints/` — goes through `services/`
- [ ] New models follow the SQLAlchemy async pattern
- [ ] New Pydantic schemas have `model_config = {"from_attributes": True}` where ORM compat is needed
- [ ] New tables have a migration — no direct schema changes without Alembic

### LLM and AI
- [ ] All LLM calls are wrapped in `try/except` with a fallback response
- [ ] Token usage is logged per request
- [ ] No LLM output is used directly in a database write without validation
- [ ] No raw profile text is exposed to third-party APIs without explicit approval

### Vector DB / Matching Engine
- [ ] Embedding model version is tagged in metadata on any new embedding record
- [ ] Hard filters (role, region, VAT) are applied before vector similarity search
- [ ] A model change is flagged explicitly — it requires full re-indexing

### Testing
- [ ] New code has unit tests
- [ ] Overall coverage remains above 70%
- [ ] Tests mock external services (LLM, vector DB, email) — no real calls in test suite
- [ ] Async test fixtures use `pytest-asyncio`

### Internationalisation
- [ ] No user-facing strings are hardcoded in Python or TypeScript
- [ ] All new UI strings have entries in the Kazakh and Russian i18n files
- [ ] Date, number, and currency formatting uses locale-aware utilities

### Conventions
- [ ] Branch name follows `feature/E{N}-{description}` or `fix/E{N}-{description}`
- [ ] Commit messages follow Conventional Commits with Epic ID
- [ ] No direct commits to `develop` or `main`

---

## Feedback Format

When giving review feedback, structure comments as:

**Blocking** — must be fixed before merge:
> [BLOCK] `app/api/v1/endpoints/survey.py:42` — Raw SQL string interpolation. Use ORM or parameterised query.

**Non-blocking** — should be addressed but will not block merge:
> [SUGGEST] `app/services/matching.py:87` — Consider extracting the filter logic into a separate function for testability.

**Positive** — acknowledge good patterns:
> [GOOD] LLM call in `app/services/agent.py` is correctly wrapped with try/except and token logging.

---

## Definition of Done (final gate before merge approval)

- [ ] All blocking review comments resolved
- [ ] CI pipeline passing (lint, type check, tests)
- [ ] Deployed to staging and tested
- [ ] PR description updated to reflect final state of changes
- [ ] Reviewed and approved by the other developer
