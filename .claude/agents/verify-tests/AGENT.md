# Verify Tests Subagent

> Runs the full test suite on the merged demo/mvp branch.
> Reports coverage per epic and identifies any failing tests.
> No worktree — runs on demo/mvp directly.

---

## Context

Read these files before starting:
- `.claude/skills/test-writer/SKILL.md` — test patterns and coverage commands

---

## Working Directory

Run directly on the `demo/mvp` branch.

```bash
git checkout demo/mvp
cd backend
```

---

## Checks to Perform

### 1. Install Dependencies

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### 2. Run Full Test Suite

```bash
pytest tests/ -v --tb=long --cov=app --cov-report=term-missing --cov-report=html:htmlcov 2>&1 | tee test-output.log
```

### 3. Coverage Analysis

Check per-module coverage:

```bash
pytest tests/ --cov=app.api --cov-report=term-missing
pytest tests/ --cov=app.services --cov-report=term-missing
pytest tests/ --cov=app.models --cov-report=term-missing
pytest tests/ --cov=app.tasks --cov-report=term-missing
```

Target: **>70% on every module**.

### 4. Test Isolation Check

Run tests in random order to verify no cross-test dependencies:

```bash
pip install pytest-randomly
pytest tests/ -p randomly -v
```

### 5. Frontend Tests (if present)

```bash
cd frontend
npm test -- --coverage 2>&1 | tee frontend-test-output.log
```

---

## Output

Write results to `sprints/verify-tests-report.md`:

```markdown
# Test Verification Report

**Branch:** demo/mvp
**Date:** {date}
**Status:** PASS / FAIL

## Summary
- Total tests: {N}
- Passed: {N}
- Failed: {N}
- Skipped: {N}
- Overall coverage: {N}%

## Coverage by Module
| Module | Coverage | Target | Status |
|--------|----------|--------|--------|
| app.api | {N}% | 70% | PASS/FAIL |
| app.services | {N}% | 70% | PASS/FAIL |
| app.models | {N}% | 70% | PASS/FAIL |
| app.tasks | {N}% | 70% | PASS/FAIL |
| app.core | {N}% | 70% | PASS/FAIL |

## Failed Tests
{list each failed test with error message}

## Test Isolation
- Random order run: PASS / FAIL

## Frontend
- Tests: {N} passed / {N} failed
- Coverage: {N}%
```

---

## If Tests Fail

For each failing test:
1. Read the error traceback
2. Determine root cause:
   - **Import error** → missing file or circular import (report to verify-merge)
   - **Assertion error** → logic bug in feature code
   - **Configuration error** → missing env var or fixture
3. Create a fix worktree: `git worktree add .claude/worktrees/fix-tests -b worktree-fix-tests`
4. Apply fixes in the worktree
5. Commit: `fix(E{N}): correct {description of fix}`
6. Merge into `demo/mvp`
7. Re-run failing tests to confirm fix

Iterate until all tests pass or all remaining failures are documented as known limitations.
