# MVP Orchestrator — Execution Plan

> Quick-reference guide for running the orchestrator manually or understanding
> the automated flow. This is the "how to launch" companion to AGENT.md.

---

## Agent Inventory (13 agents)

```
.claude/agents/
├── mvp-orchestrator/      ← YOU ARE HERE (master)
│
├── Phase 1 — Scaffold (sequential)
│   ├── scaffold-backend/      Creates FastAPI + models + Alembic
│   ├── scaffold-frontend/     Creates Next.js + pages + i18n
│   └── scaffold-docker/       Creates Docker Compose + Dockerfiles
│
├── Phase 2 — Build Features (parallel worktrees)
│   ├── build-e1-auth/         Registration, login, JWT, role
│   ├── build-e2-survey/       Survey engine, config, validation
│   ├── build-e3-matching/     Embeddings, filters, match API
│   ├── build-e4-paywall-demo/ Paywall gate, mock upgrade
│   ├── build-e6-dashboard/    Match results page, cards
│   └── seed-demo-data/        20 seed profiles + load script
│
├── Phase 3 — Verify (sequential)
│   ├── verify-merge/          File structure, imports, lint, secrets
│   ├── verify-tests/          pytest suite, coverage per module
│   └── verify-e2e/            Docker boot, full demo journey API test
│
└── Pre-existing agents (not part of MVP build)
    ├── sprint-prep/           Sprint planning briefs
    └── outreach-draft/        E5 agent outreach messages
```

---

## Dependency Graph

```
                    Phase 1 (sequential)
                    ┌────────────────────┐
                    │ scaffold-backend   │ ─── merge → demo/mvp
                    └────────┬───────────┘
                             │
                    ┌────────┴───────────┐
                    │ scaffold-frontend  │ ─── merge → demo/mvp
                    └────────┬───────────┘
                             │
                    ┌────────┴───────────┐
                    │ scaffold-docker    │ ─── merge → demo/mvp
                    └────────┬───────────┘
                             │
                    Phase 2 (parallel worktrees)
          ┌──────────────────┼──────────────────────┐
          │                  │                       │
    ┌─────┴──────┐   ┌──────┴───────┐   ┌──────────┴────────┐
    │ e1-auth    │   │ e2-survey    │   │ e3-matching       │
    │ e4-paywall │   │ e6-dashboard │   │ seed-demo-data    │
    └─────┬──────┘   └──────┬───────┘   └──────────┬────────┘
          │                  │                       │
          └──────────────────┴───────────────────────┘
                             │
                    Merge order (sequential):
                    e1 → e2 → e3 → seed → e4 → e6
                             │
                    Phase 3 (sequential)
                    ┌────────┴───────────┐
                    │ verify-merge       │
                    └────────┬───────────┘
                    ┌────────┴───────────┐
                    │ verify-tests       │
                    └────────┬───────────┘
                    ┌────────┴───────────┐
                    │ verify-e2e         │
                    └────────────────────┘
```

---

## Manual Execution Commands

If running manually (not via the orchestrator agent), here is the step-by-step:

### Setup

```bash
git checkout develop
git pull origin develop
git checkout -b demo/mvp

# Ensure worktrees directory is gitignored
echo ".claude/worktrees/" >> .gitignore
git add .gitignore
git commit -m "chore: add worktrees to gitignore"
```

### Phase 1

```bash
# 1.1 Scaffold Backend
git worktree add .claude/worktrees/scaffold-backend -b worktree-scaffold-backend
# → Run scaffold-backend agent in that worktree
# → After completion:
git checkout demo/mvp
git merge worktree-scaffold-backend --no-edit
git worktree remove .claude/worktrees/scaffold-backend
git branch -d worktree-scaffold-backend

# 1.2 Scaffold Frontend
git worktree add .claude/worktrees/scaffold-frontend -b worktree-scaffold-frontend
# → Run scaffold-frontend agent
# → Merge same pattern

# 1.3 Scaffold Docker
git worktree add .claude/worktrees/scaffold-docker -b worktree-scaffold-docker
# → Run scaffold-docker agent
# → Merge same pattern
```

### Phase 2

```bash
# Create all 6 worktrees at once
git worktree add .claude/worktrees/build-e1-auth -b worktree-build-e1-auth
git worktree add .claude/worktrees/build-e2-survey -b worktree-build-e2-survey
git worktree add .claude/worktrees/build-e3-matching -b worktree-build-e3-matching
git worktree add .claude/worktrees/build-e4-paywall-demo -b worktree-build-e4-paywall-demo
git worktree add .claude/worktrees/build-e6-dashboard -b worktree-build-e6-dashboard
git worktree add .claude/worktrees/seed-demo-data -b worktree-seed-demo-data

# → Run all 6 agents in parallel (each in their own Claude Code session)

# → After ALL complete, merge sequentially:
git checkout demo/mvp
git merge worktree-build-e1-auth --no-edit
git worktree remove .claude/worktrees/build-e1-auth && git branch -d worktree-build-e1-auth

git merge worktree-build-e2-survey --no-edit
git worktree remove .claude/worktrees/build-e2-survey && git branch -d worktree-build-e2-survey

git merge worktree-build-e3-matching --no-edit
git worktree remove .claude/worktrees/build-e3-matching && git branch -d worktree-build-e3-matching

git merge worktree-seed-demo-data --no-edit
git worktree remove .claude/worktrees/seed-demo-data && git branch -d worktree-seed-demo-data

git merge worktree-build-e4-paywall-demo --no-edit
git worktree remove .claude/worktrees/build-e4-paywall-demo && git branch -d worktree-build-e4-paywall-demo

git merge worktree-build-e6-dashboard --no-edit
git worktree remove .claude/worktrees/build-e6-dashboard && git branch -d worktree-build-e6-dashboard
```

### Phase 3

```bash
# Run on demo/mvp directly (no worktrees)
git checkout demo/mvp

# 3.1 → Run verify-merge agent
# 3.2 → Run verify-tests agent
# 3.3 → Run verify-e2e agent
```

---

## Conflict Resolution Playbook

| Conflict File | Resolution Strategy |
|--------------|---------------------|
| `backend/app/api/v1/router.py` | Combine all router includes from both sides |
| `backend/app/main.py` | Keep create_app(), merge any new middleware |
| `backend/requirements.txt` | Union of both dependency lists |
| `frontend/src/i18n/*.json` | Merge JSON keys (no overlapping keys expected) |
| `frontend/src/app/dashboard/page.tsx` | Prefer the feature branch (E6) over scaffold |
| `docker-compose.yml` | Should not conflict (only created by scaffold-docker) |
| `.env.example` | Union of both env var lists |

---

## Estimated Duration

| Phase | Agents | Estimated Time | Notes |
|-------|--------|---------------|-------|
| Phase 1 | 3 (sequential) | ~15 min | Simple scaffolding, fast |
| Phase 2 | 6 (parallel) | ~30 min | Longest agents: E3 (matching), E2 (survey) |
| Merging | 6 merges | ~10 min | Including conflict resolution |
| Phase 3 | 3 (sequential) | ~20 min | Docker boot + full journey walkthrough |
| Fixes | Variable | ~10–20 min | Depends on verification failures |
| **Total** | | **~75–95 min** | For one orchestrator session |

---

## Demo Defaults (for blocked ADRs)

The following defaults are used for the demo, bypassing open ADRs:

| ADR | Demo Default | Production Action Required |
|-----|-------------|---------------------------|
| ADR-001 (Payment) | Mock upgrade (no real payment) | Integrate Kaspi/Halyk/Stripe |
| ADR-002 (Data Residency) | Local Docker (no cloud) | Choose Kazteleport/AWS/Hybrid |
| ADR-003 (Embedding Model) | `multilingual-e5-large` (self-hosted) | Benchmark and decide |

These defaults are clearly labelled in code (comments + DEMO_MODE flag) and
do not represent production architectural decisions.
