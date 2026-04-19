# Build E1 — Auth Subagent

> Implements user registration, login, JWT tokens, and role selection.
> Runs inside an isolated worktree on top of the scaffold-backend code.

---

## Context

Read these files before starting:
- `.claude/skills/api-spec/SKILL.md` — endpoint patterns
- `.claude/skills/test-writer/SKILL.md` — test patterns and fixtures
- `.claude/context/profile-schema.md` §7 "Key User Roles" — role definitions
- `.claude/CLAUDE.md` §10 — conventions (JWT + OAuth2 auth)

---

## Working Directory

```
.claude/worktrees/build-e1-auth/
```

Work only within this path. The backend scaffold is already present.

---

## Stories to Implement

### E1-01: Email Registration
**Endpoint:** `POST /api/v1/auth/register`
**Request:** `{ email: str, password: str }`
**Response:** `201` → `{ access_token, refresh_token, token_type: "bearer" }`
**Logic:**
- Validate email format
- Check email uniqueness (409 if exists)
- Hash password with bcrypt (min 8 chars, else 422)
- Create User record (tier=free, role=null, is_active=true)
- Return JWT pair

### E1-02: Login & JWT Refresh
**Endpoint:** `POST /api/v1/auth/login`
**Request:** `{ email: str, password: str }`
**Response:** `200` → `{ access_token, refresh_token, token_type }`
**Logic:**
- Verify email exists and password matches (401 if not)
- Generate access token (expires: ACCESS_TOKEN_EXPIRE_MINUTES)
- Generate refresh token (expires: REFRESH_TOKEN_EXPIRE_DAYS)

**Endpoint:** `POST /api/v1/auth/refresh`
**Request:** `{ refresh_token: str }`
**Response:** `200` → `{ access_token, refresh_token, token_type }`
**Logic:**
- Decode refresh token (401 if expired/invalid)
- Rotate: issue new access + refresh pair
- Old refresh token becomes invalid

### E1-03: Role Selection
**Endpoint:** `PATCH /api/v1/users/me/role`
**Request:** `{ role: "buyer" | "supplier" }`
**Response:** `200` → `UserResponse`
**Logic:**
- Requires authenticated user (JWT Bearer dependency)
- Set user.role = requested role
- If user already has a submitted profile, reject with 409 ("role locked after survey")
- Role is case-insensitive in request, stored as lowercase

### Auth Dependency (shared)
Create a reusable FastAPI dependency `get_current_user`:
- Extract Bearer token from Authorization header
- Decode JWT, fetch user from DB
- Return User object (or 401 if invalid/expired)

---

## Files to Create / Modify

### New Files
```
backend/app/api/v1/endpoints/auth.py     # register, login, refresh
backend/app/api/v1/endpoints/users.py    # PATCH /users/me/role, GET /users/me
backend/app/services/auth_service.py     # Business logic: register, authenticate, refresh
backend/app/api/deps.py                  # get_current_user dependency
backend/tests/unit/test_auth_service.py  # Unit tests for auth service
backend/tests/integration/test_auth.py   # Integration tests for auth endpoints
backend/tests/integration/test_users.py  # Integration tests for user endpoints
```

### Modified Files
```
backend/app/api/v1/router.py             # Add auth and users routers
backend/app/core/security.py             # Fill in JWT + bcrypt implementations
```

---

## Test Requirements

Target: **>70% coverage** on all new code.

**Unit tests (test_auth_service.py):**
- `test_register_creates_user` — happy path
- `test_register_duplicate_email_raises` — 409 scenario
- `test_register_short_password_raises` — min 8 chars
- `test_authenticate_valid_credentials` — returns tokens
- `test_authenticate_wrong_password` — raises 401
- `test_authenticate_nonexistent_email` — raises 401
- `test_refresh_valid_token` — returns new pair
- `test_refresh_expired_token` — raises 401

**Integration tests (test_auth.py):**
- `test_register_endpoint_201` — POST /auth/register
- `test_register_duplicate_409` — same email twice
- `test_login_endpoint_200` — POST /auth/login
- `test_login_wrong_password_401`
- `test_refresh_endpoint_200` — POST /auth/refresh

**Integration tests (test_users.py):**
- `test_set_role_buyer` — PATCH /users/me/role → buyer
- `test_set_role_supplier` — PATCH /users/me/role → supplier
- `test_set_role_unauthenticated_401` — no token
- `test_get_me_200` — GET /users/me returns user data

---

## Commit

```bash
git add -A
git commit -m "feat(E1): implement registration, login, JWT auth, and role selection

- POST /auth/register with email + password (bcrypt, min 8 chars)
- POST /auth/login with JWT access + refresh tokens
- POST /auth/refresh with token rotation
- PATCH /users/me/role (buyer/supplier, locked after survey)
- get_current_user dependency for protected endpoints
- Unit + integration tests (>70% coverage target)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Output Checklist

- [ ] All three endpoints work (register, login, refresh)
- [ ] Role selection enforces buyer/supplier enum
- [ ] `get_current_user` dependency injectable into any endpoint
- [ ] Password hashed with bcrypt, never stored in plain text
- [ ] Tokens use SECRET_KEY from config (not hardcoded)
- [ ] 401 on expired/invalid tokens
- [ ] Unit tests cover all happy + error paths
- [ ] Integration tests use async client from conftest
- [ ] `pytest tests/` passes with >70% coverage on auth code
- [ ] `ruff check .` passes
- [ ] Committed with Conventional Commit format
