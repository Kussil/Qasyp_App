# Build E4 — Paywall Demo Subagent

> Implements the paywall gate (blurred results) and a mock upgrade flow for demos.
> DEMO_MODE feature flag controls mock upgrade — must be disabled in production.
> Runs inside an isolated worktree.

---

## Context

Read these files before starting:
- `.claude/skills/api-spec/SKILL.md` — endpoint patterns
- `.claude/skills/test-writer/SKILL.md` — test patterns
- `.claude/CLAUDE.md` §4 — commercial model (Free / Basic / Pro tiers)

---

## Working Directory

```
.claude/worktrees/build-e4-paywall-demo/
```

---

## Stories to Implement

### E4-01: Paywall Gate — Blurred Results
**Backend logic in `GET /api/v1/matches`** (modifies E3 endpoint):
- Free user: return `matches` with max 5 items + `total` showing full count + `has_more: true`
- Each gated match beyond top 5 returned as `{ profile_id: null, company_name: "***", match_score: null, locked: true }`
- Server-side enforcement: never return real data for gated matches

**Frontend:**
- Match cards 1–5 display normally
- Cards 6+ render as blurred/locked cards with a lock icon overlay
- Show count badge: "+{N} more partners"
- CTA button: "Unlock full list" / "Толық тізімді ашу" / "Открыть полный список"

### E4-02: Mock Upgrade Flow (Demo Only)
**Endpoint:** `POST /api/v1/demo/upgrade`
**Auth:** Requires authenticated user
**Guard:** Only available when `DEMO_MODE=true` in config
**Response:** `200` → `{ tier: "basic", message: "Upgraded (demo mode)" }`
**Logic:**
- If `DEMO_MODE` is false → return 404 (endpoint doesn't exist)
- Set `user.tier = "basic"`
- Return success with explicit "demo mode" label

**Frontend:**
- "Unlock full list" button calls `/demo/upgrade`
- On success: refresh match list (now returns all results)
- Show banner: "Demo Mode — no payment required" in distinct styling (orange/amber)
- Banner visible on all pages when `DEMO_MODE=true`

---

## Files to Create / Modify

### New Files
```
backend/app/api/v1/endpoints/demo.py              # POST /demo/upgrade
backend/app/services/tier_service.py               # upgrade_user_tier logic
backend/tests/unit/test_tier_service.py
backend/tests/integration/test_demo.py
frontend/src/components/features/paywall/
├── LockedMatchCard.tsx                            # Blurred/locked card
├── UnlockBanner.tsx                               # "+N more partners" CTA
└── DemoModeBanner.tsx                             # Amber banner for demo
frontend/src/components/features/paywall/index.ts
```

### Modified Files
```
backend/app/api/v1/router.py                       # Add demo router (conditional)
backend/app/api/v1/endpoints/matches.py             # Add gated response logic
frontend/src/app/dashboard/page.tsx                 # Integrate paywall components
frontend/src/i18n/kk.json                           # Add paywall keys
frontend/src/i18n/ru.json                           # Add paywall keys
frontend/src/i18n/en.json                           # Add paywall keys
```

---

## Critical Safety Rules

1. **`POST /demo/upgrade` MUST return 404 when DEMO_MODE is false** — this is non-negotiable
2. **Never set tier to "pro" via demo endpoint** — only "basic" upgrade in demo
3. **Gated matches MUST be enforced server-side** — frontend blurring is UX only, real data never sent
4. **DemoModeBanner must always be visible** when DEMO_MODE=true — user must know this is not real

---

## Test Requirements

**Unit tests:**
- `test_upgrade_demo_mode_true` — user tier changes to basic
- `test_upgrade_demo_mode_false` — 404 returned
- `test_free_user_matches_gated` — only 5 real results
- `test_basic_user_matches_ungated` — full results returned
- `test_gated_match_no_real_data` — locked items have null fields

**Integration tests:**
- `test_demo_upgrade_200` — with DEMO_MODE=true
- `test_demo_upgrade_404` — with DEMO_MODE=false
- `test_matches_after_upgrade` — verify full list returned

---

## Commit

```bash
git add -A
git commit -m "feat(E4): add paywall gate with blurred results and demo upgrade flow

- Free users see max 5 matches, remaining shown as locked cards
- Server-side enforcement: gated matches return null fields
- POST /demo/upgrade sets tier to basic (DEMO_MODE flag only)
- Endpoint returns 404 when DEMO_MODE=false (production safe)
- DemoModeBanner shows amber warning in demo mode
- Locked card + unlock CTA with i18n labels
- Unit + integration tests

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Output Checklist

- [ ] Free user sees max 5 real matches + locked cards for the rest
- [ ] Locked cards have null profile_id and company_name ("***")
- [ ] Demo upgrade endpoint guarded by DEMO_MODE config flag
- [ ] DEMO_MODE=false → endpoint returns 404
- [ ] Demo banner visible when DEMO_MODE=true
- [ ] i18n labels for all three languages
- [ ] Tests pass with >70% coverage
- [ ] `ruff check .` and `npm run lint` pass
