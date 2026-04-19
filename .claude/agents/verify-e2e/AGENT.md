# Verify E2E Subagent

> End-to-end verification: boots the full Docker stack and walks through
> the complete demo journey. The ultimate "does it actually work?" check.
> No worktree — runs on demo/mvp directly.

---

## Context

Read these files before starting:
- `.claude/skills/docker-compose/SKILL.md` — Docker commands
- `.claude/CLAUDE.md` §5 — architecture, data flow

---

## Working Directory

Run directly on the `demo/mvp` branch.

```bash
git checkout demo/mvp
```

---

## Checks to Perform

### 1. Docker Compose Boot

```bash
# Copy .env.example to .env (if not exists)
cp -n .env.example .env

# Build and start all services
docker compose up --build -d

# Wait for services to be healthy
docker compose ps
```

Verify all 7 services are running:
- `api` — running, healthy
- `frontend` — running
- `db` — running, healthy
- `redis` — running, healthy
- `qdrant` — running
- `celery_worker` — running
- `celery_beat` — running

If any service fails to start:
1. Check logs: `docker compose logs {service}`
2. Document the failure
3. If fixable (e.g. missing env var), fix in a worktree and re-test

### 2. Health Check

```bash
# Backend health
curl -s http://localhost:8000/health | python -m json.tool
# Expected: {"status": "ok"}

# Frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# Expected: 200
```

### 3. Run Alembic Migrations

```bash
docker compose exec api alembic upgrade head
```

Verify tables created:
```bash
docker compose exec db psql -U qasyp -d qasyp -c "\dt"
# Expected: users, business_profiles, alembic_version
```

### 4. Seed Demo Data

```bash
docker compose exec api python scripts/seed_demo_data.py
```

Verify:
```bash
docker compose exec db psql -U qasyp -d qasyp -c "SELECT COUNT(*) FROM users WHERE demo=true;"
# Expected: 20
docker compose exec db psql -U qasyp -d qasyp -c "SELECT COUNT(*) FROM business_profiles WHERE demo=true;"
# Expected: 20
```

### 5. Demo Journey Walkthrough

Execute the 8-step demo journey via API calls:

**Step 1 — Register**
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@qasyp.kz", "password": "demo12345"}' | python -m json.tool
# Save: access_token
```

**Step 2 — Set Role**
```bash
curl -s -X PATCH http://localhost:8000/api/v1/users/me/role \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"role": "buyer"}' | python -m json.tool
```

**Step 3 — Submit Survey**
```bash
curl -s -X POST http://localhost:8000/api/v1/survey/submit \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "ТОО Demo Buyer",
    "bin": "123456789012",
    "legal_entity_type": "TOO",
    "vat_registered": true,
    "vat_certificate_number": "KZ123456",
    "industry_sector": "Construction",
    "business_scope": "General construction services in Almaty region",
    "products_services": ["cement", "rebar", "concrete blocks"],
    "operating_regions": ["almaty"],
    "willing_cross_border": false,
    "annual_revenue_range": "RANGE_50M_200M",
    "growth_target": "Expand to Astana market"
  }' | python -m json.tool
# Save: profile_id
```

**Step 4 — Wait for Embedding**
```bash
# Wait a few seconds for Celery task to complete
sleep 5

# Verify embedding generated
docker compose exec db psql -U qasyp -d qasyp \
  -c "SELECT embedding_generated FROM business_profiles WHERE id='{profile_id}';"
# Expected: true
```

**Step 5 — Get Matches (Free)**
```bash
curl -s http://localhost:8000/api/v1/matches \
  -H "Authorization: Bearer {access_token}" | python -m json.tool
# Expected: max 5 matches with match_score and explanation
# Expected: has_more: true (20 supplier profiles exist)
```

**Step 6 — Verify Paywall**
Confirm response has `has_more: true` and `total > 5`.

**Step 7 — Demo Upgrade**
```bash
curl -s -X POST http://localhost:8000/api/v1/demo/upgrade \
  -H "Authorization: Bearer {access_token}" | python -m json.tool
# Expected: {"tier": "basic", "message": "Upgraded (demo mode)"}
```

**Step 8 — Get Full Matches**
```bash
curl -s "http://localhost:8000/api/v1/matches?limit=50" \
  -H "Authorization: Bearer {access_token}" | python -m json.tool
# Expected: all matching supplier profiles returned (no gating)
```

### 6. Performance Check

Time the match query:
```bash
time curl -s http://localhost:8000/api/v1/matches \
  -H "Authorization: Bearer {access_token}" > /dev/null
# Target: < 2 seconds
```

### 7. Cleanup

```bash
docker compose down -v
```

---

## Output

Write results to `sprints/verify-e2e-report.md`:

```markdown
# E2E Verification Report

**Branch:** demo/mvp
**Date:** {date}
**Status:** PASS / FAIL

## Docker Services
| Service | Status |
|---------|--------|
| api | Running / Failed |
| frontend | Running / Failed |
| db | Running / Failed |
| redis | Running / Failed |
| qdrant | Running / Failed |
| celery_worker | Running / Failed |
| celery_beat | Running / Failed |

## Demo Journey
| Step | Action | Result |
|------|--------|--------|
| 1 | Register | 201 OK / Failed |
| 2 | Set Role | 200 OK / Failed |
| 3 | Submit Survey | 201 OK / Failed |
| 4 | Embedding Generated | true / false |
| 5 | Free Matches (max 5) | OK / Failed |
| 6 | Paywall Gate Active | has_more=true / false |
| 7 | Demo Upgrade | 200 OK / Failed |
| 8 | Full Matches | OK / Failed |

## Performance
- Match query response time: {N}ms (target: <2000ms)

## Issues
{list any failures with details}
```

---

## If Steps Fail

1. Document the exact error and step number
2. Check service logs: `docker compose logs {service} --tail=50`
3. If fixable: create worktree `worktree-fix-e2e`, apply fix, merge to `demo/mvp`
4. Re-run ONLY the failing step and all subsequent steps
5. If unfixable: document as known limitation in the report
