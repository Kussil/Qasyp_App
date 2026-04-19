# Build E2 — Survey Engine Subagent

> Implements the adaptive survey Q&A flow: question config, validation, and profile save.
> Runs inside an isolated worktree.

---

## Context

Read these files before starting:
- `.claude/skills/survey-flow/SKILL.md` — full survey design, branching logic, regions
- `.claude/skills/api-spec/SKILL.md` — endpoint patterns
- `.claude/skills/test-writer/SKILL.md` — test patterns
- `.claude/context/profile-schema.md` — canonical data model (ALL profile fields)

---

## Working Directory

```
.claude/worktrees/build-e2-survey/
```

---

## Stories to Implement

### E2-01: Survey Question Config Loader
**Endpoint:** `GET /api/v1/survey/questions?role={buyer|supplier}`
**Response:** `200` → ordered list of question sections with questions
**Logic:**
- Load questions from `backend/app/data/survey_config.json`
- Filter by role (some questions differ for buyer vs supplier)
- Apply conditional logic (e.g. VAT certificate only if VAT registered)
- Validate config against JSON schema on app startup
- Return sections in order: Legal → Business Profile → Financial → Geographic

**survey_config.json structure:**
```json
{
  "sections": [
    {
      "id": "legal",
      "title": { "kk": "...", "ru": "...", "en": "Legal & Registration" },
      "questions": [
        {
          "id": "company_name",
          "type": "text",
          "label": { "kk": "...", "ru": "Название компании", "en": "Company name" },
          "required": true,
          "max_length": 200,
          "roles": ["buyer", "supplier"]
        },
        {
          "id": "bin",
          "type": "text",
          "label": { "kk": "БСН", "ru": "БИН", "en": "BIN" },
          "required": true,
          "validation": "^[0-9]{12}$",
          "roles": ["buyer", "supplier"]
        },
        {
          "id": "vat_certificate_number",
          "type": "text",
          "conditional_on": { "field": "vat_registered", "value": true },
          "required": true,
          "roles": ["buyer", "supplier"]
        }
      ]
    }
  ]
}
```

Include ALL fields from profile-schema.md as questions. Use the 19 Kazakhstan regions
from the survey-flow skill. Use the industry sector taxonomy from profile-schema.md.

### E2-02: Legal & Company Info Questions
Backend validation for Section 1 fields:
- `company_name`: required, max 200 chars
- `bin`: required, exactly 12 digits (`^[0-9]{12}$`)
- `legal_entity_type`: required, enum (TOO, IP, AO, GP, OTHER)
- `vat_registered`: required, boolean
- `vat_certificate_number`: required IF `vat_registered=true`, else optional

### E2-03: Business Profile Questions
Backend validation for Section 2 fields:
- `industry_sector`: required, from taxonomy
- `business_scope`: required, max 500 chars
- `products_services`: required, list of strings
- `operating_regions`: required, multi-select from region enum
- `volume_requirements`: optional
- `frequency`: optional, enum
- `quality_standards`: optional, list of strings
- `delivery_requirements`: optional

### E2-04: Survey Submit & Profile Save
**Endpoint:** `POST /api/v1/survey/submit`
**Request:** Full survey response body (all fields)
**Auth:** Requires authenticated user
**Response:** `201` → `{ profile_id, status: "completed" }`
**Logic:**
- Validate all required fields per role
- Apply conditional validation (VAT certificate)
- Create BusinessProfile record linked to user
- Set `user.profile_submitted = true` (prevents re-submission)
- Dispatch Celery task `generate_embedding` for the new profile
- Return profile_id

**Endpoint:** `PATCH /api/v1/survey`
**Auth:** Requires authenticated user with existing profile
**Request:** Partial update (only changed fields)
**Response:** `200` → updated ProfileResponse
**Logic:**
- Validate changed fields
- Update profile record
- Re-dispatch `generate_embedding` task (re-index required)

---

## Files to Create / Modify

### New Files
```
backend/app/data/survey_config.json              # Full survey question config
backend/app/data/survey_schema.json              # JSON schema for config validation
backend/app/api/v1/endpoints/survey.py           # GET questions, POST submit, PATCH update
backend/app/services/survey_service.py           # Config loading, validation, profile creation
backend/tests/unit/test_survey_service.py        # Unit tests
backend/tests/integration/test_survey.py         # Integration tests
```

### Modified Files
```
backend/app/api/v1/router.py                     # Add survey router
backend/app/models/user.py                       # Add profile_submitted flag if needed
```

---

## Frontend (survey page shell)

### New/Modified Files
```
frontend/src/app/onboarding/survey/page.tsx      # Multi-step survey wizard
frontend/src/components/features/survey/
├── SurveyWizard.tsx                             # Step-by-step form container
├── SurveySection.tsx                            # Renders a section of questions
├── QuestionField.tsx                            # Renders individual question by type
├── SurveyProgress.tsx                           # Progress bar (section X of 4)
└── SurveyReview.tsx                             # Review answers before submit
frontend/src/lib/survey.ts                       # Survey API calls
frontend/src/i18n/kk.json                        # Add survey keys
frontend/src/i18n/ru.json                        # Add survey keys
frontend/src/i18n/en.json                        # Add survey keys
```

**Survey UX:**
1. Display progress bar showing current section (1 of 4)
2. Render questions from config, respecting conditional logic
3. Validate client-side before moving to next section
4. Show review screen before final submit
5. Call POST /survey/submit on confirmation
6. Redirect to /dashboard on success

---

## Test Requirements

**Unit tests (test_survey_service.py):**
- `test_load_config_valid` — config loads and validates
- `test_filter_questions_buyer` — buyer sees buyer questions
- `test_filter_questions_supplier` — supplier sees supplier questions
- `test_conditional_vat_shown` — VAT certificate shown when VAT registered
- `test_conditional_vat_hidden` — VAT certificate hidden when not registered
- `test_validate_bin_valid` — 12-digit BIN passes
- `test_validate_bin_invalid` — non-12-digit fails
- `test_create_profile` — profile saved to DB
- `test_submit_triggers_embedding_task` — Celery task dispatched

**Integration tests (test_survey.py):**
- `test_get_questions_buyer_200` — returns buyer question set
- `test_get_questions_unauthenticated_401`
- `test_submit_survey_201` — full valid submission
- `test_submit_survey_missing_required_422` — missing company_name
- `test_submit_survey_invalid_bin_422` — wrong BIN format
- `test_submit_duplicate_409` — re-submission blocked
- `test_patch_survey_200` — partial update works
- `test_patch_triggers_re_embedding` — Celery re-index task dispatched

---

## Commit

```bash
git add -A
git commit -m "feat(E2): implement survey engine with config loader and profile save

- GET /survey/questions with role-based filtering and conditional logic
- POST /survey/submit with full validation and Celery embedding trigger
- PATCH /survey for partial profile updates with re-indexing
- survey_config.json with all fields from profile-schema.md
- Multi-step survey wizard frontend component
- i18n labels for Kazakh, Russian, English
- BIN validation (12 digits), conditional VAT field
- Unit + integration tests (>70% coverage)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Output Checklist

- [ ] `survey_config.json` covers ALL fields from profile-schema.md
- [ ] Config validates against JSON schema on startup
- [ ] Buyer and supplier get role-appropriate questions
- [ ] VAT certificate conditional logic works
- [ ] BIN validation: exactly 12 digits
- [ ] Profile saved to DB with correct foreign key to user
- [ ] Celery task `generate_embedding` dispatched on submit
- [ ] Re-submit blocked (409)
- [ ] PATCH triggers re-embedding
- [ ] Frontend wizard shows progress, validates, reviews before submit
- [ ] i18n keys added for all three languages
- [ ] Tests pass with >70% coverage
- [ ] `ruff check .` and `npm run lint` pass
