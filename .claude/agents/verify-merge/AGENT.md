# Verify Merge Subagent

> Post-merge verification: checks that the demo/mvp branch is structurally sound
> after all feature worktrees have been merged. No worktree — runs on demo/mvp directly.

---

## Context

Read these files before starting:
- `.claude/skills/code-review/SKILL.md` — review checklist
- `.claude/CLAUDE.md` §10 — conventions

---

## Working Directory

Run directly on the `demo/mvp` branch (not in a worktree).

```bash
git checkout demo/mvp
```

---

## Checks to Perform

### 1. File Structure Verification

Confirm ALL expected directories exist:

```
backend/
├── app/
│   ├── main.py
│   ├── core/config.py
│   ├── core/security.py
│   ├── core/database.py
│   ├── models/user.py
│   ├── models/profile.py
│   ├── schemas/auth.py
│   ├── schemas/profile.py
│   ├── schemas/match.py
│   ├── api/v1/router.py
│   ├── api/v1/endpoints/auth.py
│   ├── api/v1/endpoints/survey.py
│   ├── api/v1/endpoints/matches.py
│   ├── api/v1/endpoints/demo.py
│   ├── api/v1/endpoints/health.py
│   ├── api/deps.py
│   ├── services/auth_service.py
│   ├── services/survey_service.py
│   ├── services/matching_service.py
│   ├── services/embedding_service.py
│   ├── services/explanation_service.py
│   ├── services/tier_service.py
│   ├── tasks/celery_app.py
│   ├── tasks/embedding_tasks.py
│   └── data/survey_config.json
├── alembic/
├── tests/
├── requirements.txt
├── Dockerfile
└── pyproject.toml
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── auth/login/page.tsx
│   │   ├── auth/register/page.tsx
│   │   ├── onboarding/survey/page.tsx
│   │   ├── dashboard/page.tsx
│   │   └── dashboard/layout.tsx
│   ├── components/features/
│   ├── lib/api.ts
│   ├── i18n/
│   └── types/
├── package.json
├── Dockerfile
└── tailwind.config.ts
docker-compose.yml
.env.example
```

Report any missing files as **MISSING: {path}**.

### 2. Import Chain Verification

For each Python file, verify:
- No `ImportError` — all relative imports resolve
- Run: `cd backend && python -c "from app.main import create_app; print('OK')"`
- Run: `cd backend && python -c "from app.models.user import User; print('OK')"`
- Run: `cd backend && python -c "from app.models.profile import BusinessProfile; print('OK')"`

For frontend:
- Run: `cd frontend && npx tsc --noEmit` (TypeScript type check)

### 3. Lint Check

```bash
cd backend && ruff check .
cd frontend && npm run lint
```

Report any errors. Auto-fix if possible (`ruff check --fix .`).

### 4. Secrets Scan

```bash
grep -rn "sk-ant-" backend/ frontend/ --include="*.py" --include="*.ts" --include="*.tsx"
grep -rn "password.*=" backend/ --include="*.py" | grep -v "hashed_password" | grep -v "test_"
grep -rn "SECRET_KEY.*=" backend/ --include="*.py" | grep -v "config.py" | grep -v "settings"
```

Any match is a **BLOCK** finding.

### 5. Convention Check

- All commit messages on `demo/mvp` follow Conventional Commits with Epic ID scope
- `v1/router.py` includes all routers (auth, users, survey, matches, demo, health)
- No `print()` statements in production code (use `logging`)
- No TODO without issue reference
- `.env` is NOT committed (check `.gitignore`)

---

## Output

Write results to `sprints/verify-merge-report.md`:

```markdown
# Merge Verification Report

**Branch:** demo/mvp
**Date:** {date}
**Status:** PASS / FAIL

## File Structure
- [x] All expected files present
- [ ] MISSING: {file} (if any)

## Import Chain
- [x] Backend imports OK
- [x] Frontend TypeScript OK

## Lint
- [x] ruff: 0 errors
- [x] eslint: 0 errors

## Secrets Scan
- [x] No hardcoded secrets found

## Convention Check
- [x] Commit messages follow conventions
- [x] All routers registered
- [x] No print() in production code

## Issues Found
{list any issues with severity}
```

---

## If Issues Found

For each issue:
1. Classify severity: **BLOCK** (must fix) or **WARN** (can proceed)
2. For BLOCK issues: create a fix worktree, apply fix, merge back to demo/mvp
3. For WARN issues: log in report for future cleanup
