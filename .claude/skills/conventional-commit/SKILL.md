---
name: conventional-commit
description: Draft and validate commit messages for Qasyp App following the Conventional Commits standard with Epic IDs. Use when staging changes and writing a commit, or to check whether an existing message is correctly formatted.
---

# Conventional Commit

Drafts and validates commit messages following the Qasyp App convention: Conventional Commits format with an Epic ID in the scope field.

## When to Use

- You are about to commit and need to write the message
- You want to check whether a commit message is correctly formatted
- You are squashing commits into a single PR merge message

---

## Format

```
{type}({scope}): {short description}

{optional body}

{optional footer}
```

### Type

| Type       | Use when                                              |
|------------|-------------------------------------------------------|
| `feat`     | Adding a new feature or capability                    |
| `fix`      | Fixing a bug                                          |
| `test`     | Adding or updating tests                              |
| `refactor` | Restructuring code without changing behaviour         |
| `perf`     | Improving performance                                 |
| `docs`     | Documentation only changes                            |
| `chore`    | Maintenance tasks: deps, config, build, CI            |
| `style`    | Formatting, whitespace — no logic changes             |

### Scope

Always use the Epic ID as scope:

| Scope | Epic                   |
|-------|------------------------|
| `E1`  | User Onboarding & Auth |
| `E2`  | Survey Engine          |
| `E3`  | Matching Engine (RAG)  |
| `E4`  | Freemium & Paywall     |
| `E5`  | AI Agent Outreach      |
| `E6`  | User Dashboard         |
| `E7`  | Admin & Analytics      |

If the change spans multiple epics or is infrastructure-wide, use the most relevant one. For project-wide config changes with no epic, use `chore` with a descriptive scope (e.g., `chore(ci)`, `chore(deps)`).

### Short Description

- Imperative mood: "add", "fix", "remove" — not "added", "fixed", "removing"
- Lowercase, no trailing period
- Maximum 72 characters including type and scope
- Describes what the commit does, not what you did

### Body (optional)

- Explain *why* the change was made, not *what* — the diff shows what
- Wrap at 72 characters
- Separate from subject line with a blank line

### Footer (optional)

```
BREAKING CHANGE: {description of breaking change}
Closes #{issue-number}
```

---

## Examples

**Simple feature:**
```
feat(E2): add VAT status field to onboarding survey
```

**Bug fix with explanation:**
```
fix(E1): correct JWT refresh token expiry calculation

Token expiry was being calculated from creation time rather than
issue time, causing premature session invalidation for users who
logged in via OAuth2.
```

**Test addition:**
```
test(E3): add unit tests for vector similarity filter logic
```

**Infrastructure:**
```
chore(ci): add ruff linting step to GitHub Actions workflow
```

**Breaking change:**
```
feat(E3): replace pgvector with Qdrant as vector store

BREAKING CHANGE: Profile embeddings must be re-indexed after
this change. Run scripts/reindex_embeddings.py before deploying.
```

**Closes an issue:**
```
fix(E4): resolve Kaspi payment webhook signature mismatch

Closes #47
```

---

## Drafting a Commit Message from a Diff

When given a `git diff` output:

1. Identify which epic the changed files belong to (check `app/api/v1/endpoints/`, `app/services/`, `app/models/`, etc.)
2. Determine the type: is this new behaviour (`feat`), a correction (`fix`), structural change (`refactor`), or other?
3. Write a subject line in imperative mood, under 72 characters
4. If the change is non-obvious, add a body explaining the reasoning
5. Add footer if there is a breaking change or linked issue

---

## Validation Checklist

Before finalising a commit message, verify:

- [ ] Type is one of the allowed values
- [ ] Scope is an Epic ID (`E1`–`E7`) or an infrastructure scope (`ci`, `deps`, `docker`)
- [ ] Subject line is imperative mood, lowercase, no trailing period
- [ ] Subject line is 72 characters or fewer
- [ ] Body (if present) is separated from subject by a blank line
- [ ] `BREAKING CHANGE:` footer is present if the change breaks existing behaviour
- [ ] No references to internal chat messages, ticket summaries, or debugging notes
