# Seed Demo Data Subagent

> Creates 20 realistic Kazakhstani business profiles for demo purposes.
> Generates embeddings so the matching engine returns meaningful results.
> Runs inside an isolated worktree.

---

## Context

Read these files before starting:
- `.claude/context/profile-schema.md` — canonical data model (all fields)
- `.claude/skills/rag-pipeline/SKILL.md` — embedding patterns
- `.claude/skills/survey-flow/SKILL.md` — regions list, industry taxonomy

---

## Working Directory

```
.claude/worktrees/seed-demo-data/
```

---

## What to Create

### Seed Script
**File:** `backend/scripts/seed_demo_data.py`

Standalone script (runnable via `python scripts/seed_demo_data.py` or `docker compose exec api python scripts/seed_demo_data.py`).

### Profile Set

Create **10 Buyer** + **10 Supplier** profiles across **5 industries**:

| Industry          | Buyers | Suppliers |
|-------------------|--------|-----------|
| Construction      | 2      | 2         |
| Food & Agriculture| 2      | 2         |
| IT & Technology   | 2      | 2         |
| Mining & Energy   | 2      | 2         |
| Logistics         | 2      | 2         |

### Profile Realism Rules

1. **Company names** — realistic Kazakh ТОО/ИП names (Russian transliteration):
   - e.g. `ТОО "Алматы Құрылыс"`, `ИП "Нурбеков"`, `ТОО "ТехноСервис Астана"`
2. **BIN** — 12 random digits (format valid, not real)
3. **Operating regions** — spread across Kazakhstan (not all Almaty):
   - Almaty, Astana, Shymkent, Karaganda, Atyrau, Aktobe, Pavlodar, etc.
4. **Products/services** — specific to industry and role:
   - Construction Buyer: "cement, rebar, concrete blocks"
   - Construction Supplier: "ready-mix concrete, steel reinforcement"
5. **Business scope** — 1–2 sentences in Russian (realistic B2B description)
6. **Revenue ranges** — varied across brackets
7. **Cross-border** — mix of true/false (mostly false for realism)
8. **Quality standards** — industry-appropriate (GOST, ISO 9001, HACCP, etc.)

### Matching Pairs

Design profiles so certain buyer-supplier pairs produce high match scores:

| Buyer | Supplier | Expected Score | Why |
|-------|----------|---------------|-----|
| Construction Buyer (Almaty) | Construction Supplier (Almaty) | >85% | Same industry, same region, complementary products |
| Food Buyer (Astana) | Food Supplier (Shymkent) | ~70% | Same industry, different region but cross_border=true |
| IT Buyer (Almaty) | IT Supplier (Karaganda) | ~65% | Same industry, different region, no cross_border |
| Mining Buyer (Atyrau) | Mining Supplier (Atyrau) | >80% | Same industry, same region (oil hub) |

These expected pairs make the demo compelling — the matching engine returns
sensible, explainable results.

### Script Logic

```python
# 1. Create User records for each profile (demo users, no real auth)
# 2. Create BusinessProfile records with all fields populated
# 3. Generate embeddings for each profile
# 4. Upsert embeddings into Qdrant
# 5. Tag all records with demo=true
# 6. Print summary of created profiles
```

**Idempotency:** Script checks for existing demo profiles and deletes them before re-seeding.
This allows running the script multiple times safely.

### Data File
Also create `backend/app/data/demo_profiles.json` — the 20 profiles as structured JSON,
so they can be version-controlled and reviewed independently of the script.

---

## Files to Create

```
backend/scripts/seed_demo_data.py          # Seed script (standalone)
backend/scripts/__init__.py
backend/app/data/demo_profiles.json        # 20 profiles as JSON
backend/tests/unit/test_seed_data.py       # Verify profiles are valid
```

---

## Test Requirements

- `test_demo_profiles_valid_schema` — all 20 profiles validate against profile-schema fields
- `test_demo_profiles_buyer_supplier_balance` — 10 buyers + 10 suppliers
- `test_demo_profiles_industry_coverage` — all 5 industries represented
- `test_demo_profiles_region_diversity` — at least 5 different regions used
- `test_demo_profiles_bin_format` — all BINs match `^[0-9]{12}$`

---

## Commit

```bash
git add -A
git commit -m "feat(demo): add 20 seed business profiles for demo matching

- 10 Buyer + 10 Supplier profiles across 5 industries
- Realistic Kazakh company names, BINs, and operating regions
- Designed match pairs for compelling demo results
- Seed script with idempotent re-seeding (deletes demo=true first)
- demo_profiles.json for version-controlled review
- Validation tests for schema compliance and diversity

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Output Checklist

- [ ] 20 profiles: 10 Buyer + 10 Supplier
- [ ] 5 industries covered with 4 profiles each
- [ ] At least 5 different Kazakhstan regions used
- [ ] Company names are realistic Kazakh business names
- [ ] BINs are valid 12-digit format
- [ ] Business scope and products written in Russian
- [ ] Profiles designed so known buyer-supplier pairs match well
- [ ] All profiles tagged `demo=true`
- [ ] Script is idempotent (safe to re-run)
- [ ] Tests validate profile data integrity
- [ ] Committed with Conventional Commit format
