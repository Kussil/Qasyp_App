# Build E3 — Matching Engine Subagent

> Implements the RAG matching pipeline: embeddings, hard filters, vector search,
> match scoring, and LLM-generated explanations.
> Runs inside an isolated worktree.

---

## Context

Read these files before starting:
- `.claude/skills/rag-pipeline/SKILL.md` — embedding patterns, Qdrant/pgvector, Celery tasks
- `.claude/skills/api-spec/SKILL.md` — endpoint patterns
- `.claude/skills/test-writer/SKILL.md` — test patterns
- `.claude/context/profile-schema.md` — embedding strategy, hard-filter fields, match logic
- `docs/ADR-003-embedding-model.md` — model options (use multilingual-e5-large as demo default)

---

## Working Directory

```
.claude/worktrees/build-e3-matching/
```

---

## Stories to Implement

### E3-01: Embedding Pipeline (Celery Task)
**Task:** `generate_embedding`
**Queue:** `embeddings`
**Trigger:** Called by survey submit (E2-04) and survey update (PATCH)
**Logic:**
1. Fetch BusinessProfile by profile_id
2. Concatenate embedding text fields (from profile-schema.md):
   `business_scope + products_services + industry_sector + quality_standards + preferred_partner_profile + growth_target`
3. Generate embedding vector using the configured model
4. Upsert into Qdrant collection with payload:
   ```json
   {
     "profile_id": "uuid",
     "user_id": "uuid",
     "role": "buyer|supplier",
     "operating_regions": ["almaty", "astana"],
     "willing_cross_border": false,
     "annual_revenue_range": "RANGE_50M_200M",
     "embedding_model_version": "multilingual-e5-large",
     "demo": false
   }
   ```
5. Set `profile.embedding_generated = true`

**Embedding Model Wrapper:**
Create `backend/app/services/embedding_service.py`:
- `get_embedding(text: str) -> list[float]`
- Uses `sentence-transformers` with model from `EMBEDDING_MODEL_VERSION` config
- Wrapped in try/except — on failure, log error and set `embedding_generated = false`
- Log token/character count per call
- Model loaded once at import time (singleton pattern)

**For demo:** Use `multilingual-e5-large` via sentence-transformers. This resolves ADR-003
temporarily for the demo without committing to a production choice.

### E3-02: Hard-Filter Pre-Screening
**Function:** `apply_hard_filters(user_profile, candidates) -> filtered_candidates`
**Logic (from profile-schema.md):**
1. **Role complementarity:** If user is Buyer → return only Supplier profiles (and vice versa)
2. **Region overlap:** User's `operating_regions` must intersect with candidate's `operating_regions`
   — UNLESS either party has `willing_cross_border = true` (skip region filter)
3. **Revenue range (optional):** If enabled, filter to compatible revenue brackets

Implemented as Qdrant filter conditions (not post-retrieval filtering):
```python
must = [
    FieldCondition(key="role", match=MatchValue(value=complementary_role)),
]
should = [
    # Region overlap OR cross-border willingness
]
```

### E3-03: Match Query Endpoint
**Endpoint:** `GET /api/v1/matches`
**Auth:** Requires authenticated user with completed profile
**Query params:** `limit` (default 5, max 50), `offset` (default 0)
**Response:** `200` → `MatchListResponse`
```json
{
  "matches": [
    {
      "profile_id": "uuid",
      "company_name": "ТОО Алматы Строй",
      "industry_sector": "Construction",
      "operating_regions": ["almaty"],
      "match_score": 0.87,
      "explanation": "Strong match based on shared construction industry focus..."
    }
  ],
  "total": 15,
  "has_more": true
}
```
**Logic:**
1. Get current user's profile and embedding
2. Apply hard filters as Qdrant query conditions
3. Run cosine similarity search (top `limit` results)
4. For free users: return only top 5 (gate server-side)
5. For basic/pro users: return full `limit`
6. Cache results in Redis (key: `matches:{user_id}`, TTL: 1 hour)
7. Response time target: < 2 seconds (p95)

### E3-04: Match Score Explanation
**Function:** `generate_explanation(user_profile, match_profile) -> str`
**Logic:**
1. Build a structured prompt with both profiles' key fields
2. Call Anthropic Claude API to generate 1–2 sentence explanation
3. Prompt instructs: explain WHY these businesses are a good match, referencing specific fields
4. **Wrapped in try/except** — on failure, fall back to field-based template:
   `"Matched on {industry_sector} in {shared_regions} with complementary {role} profile."`
5. Log token usage per call
6. Cache explanation per match pair (Redis, TTL: 24 hours)

**LLM Prompt Template:**
```
You are a B2B matching assistant. Given two business profiles, explain in 1-2 sentences
why they are a good match. Reference specific details from their profiles.
Do not fabricate information. Use only the fields provided.

Buyer profile: {buyer_fields}
Supplier profile: {supplier_fields}
Match score: {score}

Explanation:
```

---

## Files to Create / Modify

### New Files
```
backend/app/services/embedding_service.py        # Embedding model wrapper
backend/app/services/matching_service.py          # Hard filters, vector search, ranking
backend/app/services/explanation_service.py       # LLM match explanation
backend/app/tasks/embedding_tasks.py              # Celery task: generate_embedding
backend/app/api/v1/endpoints/matches.py           # GET /matches
backend/tests/unit/test_embedding_service.py
backend/tests/unit/test_matching_service.py
backend/tests/rag/test_hard_filters.py            # Filter logic tests
backend/tests/integration/test_matches.py
```

### Modified Files
```
backend/app/api/v1/router.py                      # Add matches router
backend/app/tasks/celery_app.py                    # Register embedding tasks
backend/requirements.txt                           # Add sentence-transformers, anthropic
```

### Additional Dependency
Add to `requirements.txt`:
```
sentence-transformers>=2.7.0
torch>=2.3.0
```

---

## Test Requirements

**Unit tests (test_embedding_service.py):**
- `test_get_embedding_returns_vector` — valid text → float list
- `test_get_embedding_empty_text` — handles empty gracefully
- `test_embedding_model_version_tag` — version matches config

**Unit tests (test_matching_service.py):**
- `test_build_filter_buyer_targets_suppliers` — role complementarity
- `test_build_filter_supplier_targets_buyers`
- `test_region_filter_overlap` — only matching regions
- `test_region_filter_cross_border_skip` — cross-border bypasses region
- `test_cache_hit_returns_cached` — Redis cache works
- `test_free_user_limited_to_5` — tier gate enforced

**RAG tests (test_hard_filters.py):**
- `test_buyer_never_matches_buyer`
- `test_supplier_never_matches_supplier`
- `test_cross_border_includes_all_regions`
- `test_no_overlap_no_results` — disjoint regions, no cross-border

**Integration tests (test_matches.py):**
- `test_get_matches_200` — authenticated user with profile
- `test_get_matches_no_profile_400` — user without profile
- `test_get_matches_unauthenticated_401`
- `test_matches_include_explanation` — explanation field present
- `test_matches_cached` — second call hits Redis

---

## Commit

```bash
git add -A
git commit -m "feat(E3): implement RAG matching engine with embeddings and explanations

- Celery task: generate_embedding using multilingual-e5-large
- Qdrant upsert with role, region, and model version payload
- Hard filters: role complementarity + region overlap + cross-border
- GET /matches with tier-gated results and Redis caching
- LLM-generated match explanations via Claude API (with fallback)
- Embedding model version tracked per profile
- Unit + RAG + integration tests (>70% coverage)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Output Checklist

- [ ] Embedding service loads model and generates vectors
- [ ] `EMBEDDING_MODEL_VERSION` read from config, stored in Qdrant payload
- [ ] Celery task fires on profile save and update
- [ ] Hard filters enforce role complementarity
- [ ] Region filter respects `willing_cross_border`
- [ ] Free users see max 5 matches (server-side enforcement)
- [ ] Redis cache with 1-hour TTL
- [ ] LLM explanation wrapped in try/except with template fallback
- [ ] Token usage logged per explanation call
- [ ] All tests pass with >70% coverage on E3 code
- [ ] `ruff check .` passes
