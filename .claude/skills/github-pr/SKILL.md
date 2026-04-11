---
name: github-pr
description: Manage the full pull request lifecycle for Qasyp App. Use when creating branches, opening PRs, writing PR descriptions, preparing for merge, or resolving conflicts. Enforces the project's branching convention and Conventional Commits format.
---

# GitHub PR Manager

Handles branch creation, pull request drafting, pre-merge checks, and conflict resolution following Qasyp App's git conventions.

## When to Use

- Starting work on a new feature, fix, or task
- Opening a pull request from a feature branch into `develop`
- Reviewing a PR before merge
- Resolving a merge conflict
- Checking the status of open PRs

---

## Branching Convention

```
main          — protected, production-ready only
develop       — integration branch, all feature PRs target this
feature/E{N}-{short-description}   — active feature work
fix/E{N}-{short-description}       — bug fixes
chore/{short-description}          — non-functional changes (docs, config, deps)
```

**Examples:**
```
feature/E2-adaptive-survey-branching
feature/E3-qdrant-embedding-pipeline
fix/E1-jwt-token-expiry
chore/update-docker-compose-redis
```

---

## Creating a Branch

```bash
# Always branch from develop, never from main
git checkout develop
git pull origin develop
git checkout -b feature/E{N}-{short-description}
```

---

## Commit Message Format

Follow Conventional Commits with Epic ID in scope:

```
{type}(E{N}): {short imperative description}

{optional body explaining why, not what}

{optional footer: BREAKING CHANGE or closes #issue}
```

**Types:** `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `perf`

**Examples:**
```
feat(E2): add adaptive survey branching logic
fix(E1): correct JWT token expiry on refresh
test(E3): add unit tests for vector similarity scoring
chore(E7): update docker-compose redis version
```

---

## Opening a Pull Request

### PR Title
Use the same format as commit messages:
```
feat(E2): add adaptive survey branching logic
```

### PR Description Template

```markdown
## Summary
Brief description of what this PR does and why.

## Changes
- List of key changes made
- Keep it specific and factual

## Epic
E{N} — {Epic Name}

## Testing
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Tested on local Docker environment
- [ ] No hardcoded secrets introduced
- [ ] i18n strings added for any new UI copy (Kazakh + Russian)

## Definition of Done
- [ ] Code reviewed by the other developer
- [ ] All tests passing in CI
- [ ] Deployed to staging and verified
- [ ] Acceptance criteria from user story met
- [ ] OpenAPI docs updated if endpoints changed

## Related
- Closes #issue-number (if applicable)
- Related ADR: docs/ADR-00{N}.md (if applicable)
```

---

## Pre-Merge Checklist

Run through this before approving any PR into `develop`:

```bash
# 1. Pull latest develop into the feature branch and resolve any conflicts
git fetch origin
git rebase origin/develop

# 2. Run tests
pytest --cov=app --cov-report=term-missing

# 3. Check for secrets or env vars accidentally committed
git log --all --full-history -- "*.env" "*.pem" "*.key"

# 4. Lint
ruff check app/
mypy app/

# 5. Verify no direct commits to main or develop
git log --oneline origin/develop..HEAD
```

---

## Merging into develop

```bash
# Preferred: squash merge for clean history
gh pr merge {PR-number} --squash --delete-branch

# Or via GitHub UI: "Squash and merge"
```

---

## Conflict Resolution

If a rebase or merge produces conflicts:

1. Identify conflicting files:
```bash
git status | grep "both modified"
```

2. Open each conflicting file. Conflicts look like:
```
<<<<<<< HEAD (develop)
existing code
=======
incoming code from feature branch
=======
>>>>>>> feature/E{N}-description
```

3. Resolve by keeping the correct version (or combining both where appropriate).

4. Mark resolved and continue:
```bash
git add {resolved-file}
git rebase --continue   # if rebasing
# or
git commit              # if merging
```

---

## Two-Developer Workflow

Since two developers are working simultaneously:

- **Never push directly to `develop` or `main`** — always via PR
- **Assign PRs to each other** for review before merging
- **Communicate before touching shared files** (e.g., `CLAUDE.md`, `profile-schema.md`, `docker-compose.yml`)
- **Use worktree skill** for experimental work that should not affect the shared branch
- **Pull `develop` at the start of every session** to avoid long-running divergence
