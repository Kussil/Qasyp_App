# MVP Orchestrator Agent

> Master agent that coordinates subagents to build the Qasyp App Demo MVP.
> Each subagent works in an isolated git worktree. The orchestrator merges
> results into `demo/mvp` and runs verification.

---

## Purpose

Build a stakeholder-ready Demo MVP by orchestrating subagents across isolated
worktrees. The demo journey: **Register → Survey → Match → Results → Paywall gate**.

---

## Prerequisites

Before running this agent, ensure:

1. You are on the `develop` branch with a clean working tree (`git status` is clean)
2. Docker is available (`docker compose version` succeeds)
3. Python 3.11+ and Node.js 18+ are installed
4. The `.claude/` folder exists with all skills and context files

---

## Execution Plan

The orchestrator runs **three phases** sequentially. Within each phase,
subagents that have no mutual dependencies run **in parallel worktrees**.

### Phase 1 — Scaffold (sequential, then merge)

These three subagents create the empty project skeleton. They must run
**sequentially** because the frontend and Docker scaffolds depend on the
backend folder structure.

| Order | Subagent             | Worktree Branch              | What It Creates                                    |
|-------|----------------------|------------------------------|----------------------------------------------------|
| 1.1   | `scaffold-backend`   | `worktree-scaffold-backend`  | `backend/` — FastAPI app, models, config, Alembic   |
| 1.2   | `scaffold-frontend`  | `worktree-scaffold-frontend` | `frontend/` — Next.js app, pages, components        |
| 1.3   | `scaffold-docker`    | `worktree-scaffold-docker`   | `docker-compose.yml`, `.env.example`, Dockerfiles    |

**After each subagent completes**, merge its worktree into `demo/mvp`:

```bash
# After scaffold-backend completes:
git checkout demo/mvp
git merge worktree-scaffold-backend --no-edit
git worktree remove .claude/worktrees/scaffold-backend
git branch -d worktree-scaffold-backend

# Repeat for scaffold-frontend, then scaffold-docker
```

### Phase 2 — Build Features (parallel worktrees, then sequential merge)

These subagents implement the actual features. They can run **in parallel**
because each works in its own worktree on non-overlapping files.

| Subagent                | Worktree Branch                  | Epic | What It Builds                                          |
|-------------------------|----------------------------------|------|---------------------------------------------------------|
| `build-e1-auth`         | `worktree-build-e1-auth`         | E1   | Registration, login, JWT, role selection                 |
| `build-e2-survey`       | `worktree-build-e2-survey`       | E2   | Survey config, question loader, validation, submit flow  |
| `build-e3-matching`     | `worktree-build-e3-matching`     | E3   | Embedding pipeline, hard filters, match API, explanations|
| `build-e4-paywall-demo` | `worktree-build-e4-paywall-demo` | E4   | Paywall gate, mock upgrade (DEMO_MODE flag)              |
| `build-e6-dashboard`    | `worktree-build-e6-dashboard`    | E6   | Match results page, free shortlist, full list views      |
| `seed-demo-data`        | `worktree-seed-demo-data`        | —    | 20 seed profiles + load script                           |

**Spawn all six subagents simultaneously.** Each works in its own worktree.

**Merge order matters** (to resolve dependencies cleanly):

```
1. build-e1-auth       (no dependencies — merge first)
2. build-e2-survey     (depends on E1 user model)
3. build-e3-matching   (depends on E2 profile model)
4. seed-demo-data      (depends on E3 embedding pipeline)
5. build-e4-paywall-demo (depends on E3 match endpoint)
6. build-e6-dashboard  (depends on E3 + E4 APIs)
```

For each merge:
```bash
git checkout demo/mvp
git merge worktree-build-e1-auth --no-edit
# Resolve conflicts if any (prefer incoming for new files)
git worktree remove .claude/worktrees/build-e1-auth
git branch -d worktree-build-e1-auth
```

**If a merge conflict occurs:**
1. Identify conflicting files with `git diff --name-only --diff-filter=U`
2. For new files added by both sides — keep both
3. For shared files (e.g. `backend/app/main.py` router imports) — combine both additions
4. After resolving, `git add .` and `git commit -m "merge(demo): integrate {epic} into demo/mvp"`

### Phase 3 — Verify (sequential)

Run verification subagents **one at a time** on the merged `demo/mvp` branch.

| Order | Subagent          | What It Checks                                         |
|-------|-------------------|--------------------------------------------------------|
| 3.1   | `verify-merge`    | All expected files exist, no broken imports, ruff lint  |
| 3.2   | `verify-tests`    | `pytest` passes, coverage > 70% per epic               |
| 3.3   | `verify-e2e`      | Docker Compose boots, API responds, full demo journey   |

If a verification subagent reports failures:
1. Read the failure output
2. Create a fix in a new worktree `worktree-fix-{issue}`
3. Apply the fix, merge into `demo/mvp`
4. Re-run the failed verification

---

## Orchestrator Prompt

You are the MVP Orchestrator for Qasyp App. Your job is to coordinate the
full build of the Demo MVP by running subagents in isolated git worktrees.

### Step-by-step execution:

**Step 0 — Setup**
```bash
git checkout develop
git pull origin develop
git checkout -b demo/mvp
git push -u origin demo/mvp
```

Add `.claude/worktrees/` to `.gitignore` if not already present.

**Step 1 — Phase 1: Scaffold**

Run subagents sequentially. For each:
1. Create worktree: `git worktree add .claude/worktrees/{name} -b worktree-{name}`
2. Invoke subagent: `Task` tool with the agent's AGENT.md prompt, working directory set to the worktree path
3. Wait for completion
4. Return to root, merge into `demo/mvp`, clean up worktree

Order: `scaffold-backend` → `scaffold-frontend` → `scaffold-docker`

**Step 2 — Phase 2: Build Features**

Spawn **all six** build subagents in parallel using `Task` tool:
- Each subagent gets its own worktree created beforehand
- Each subagent's prompt instructs it to work ONLY within its worktree path
- Each subagent commits its work before finishing

After ALL six complete, merge sequentially in dependency order:
`e1-auth` → `e2-survey` → `e3-matching` → `seed-demo-data` → `e4-paywall-demo` → `e6-dashboard`

**Step 3 — Phase 3: Verify**

Run verification subagents sequentially on the merged `demo/mvp` branch:
`verify-merge` → `verify-tests` → `verify-e2e`

Fix any failures by creating fix worktrees and re-merging.

**Step 4 — Report**

Output a summary to `sprints/demo-mvp-build-report.md`:
- List of all subagents run and their status (success/failed/fixed)
- Files created per epic
- Test coverage summary
- Docker Compose boot status
- Any unresolved issues or known limitations

### Rules

1. **Never push to `main` or `develop`** — all work goes to `demo/mvp`
2. **Every subagent must commit** before its worktree is merged
3. **Use Conventional Commits** — `feat(E{N}): {description}` for features, `fix(demo): {description}` for fixes
4. **Read the relevant skill** before each subagent task (e.g. read `/api-spec/SKILL.md` before scaffold-backend)
5. **Read `.claude/context/profile-schema.md`** — this is the single source of truth for the data model
6. **No hardcoded secrets** — use environment variables from `.env`
7. **All LLM calls** wrapped in try/except with fallback
8. **Agent outreach actions** must have `approved_by_user: false` at draft stage
9. **Log all decisions** — if you make an architectural choice (e.g. picking multilingual-e5-large for demo), document it in the build report

---

## Inputs

| Source | What to Read |
|--------|-------------|
| `.claude/CLAUDE.md` | Full project spec, epics, conventions |
| `.claude/context/profile-schema.md` | Canonical data model (source of truth) |
| `.claude/skills/*` | Patterns for API, RAG, survey, tests, docker, etc. |
| `docs/ADR-*.md` | Open architectural decisions (inform defaults for demo) |
| `qasyp-backlog.xlsx` → "Demo MVP" sheet | Story list, acceptance criteria, sprint assignments |

## Output

| Artifact | Location |
|----------|----------|
| Demo MVP branch | `demo/mvp` (git branch) |
| Build report | `sprints/demo-mvp-build-report.md` |
| All application code | `backend/`, `frontend/`, `docker-compose.yml` |
