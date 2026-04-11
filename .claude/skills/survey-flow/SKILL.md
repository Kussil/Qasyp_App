---
name: survey-flow
description: Design, generate, and validate the adaptive onboarding survey for Qasyp App (E2). Use when building survey question flows, validating field schemas, generating survey configs, or checking that collected data aligns with the business profile model.
---

# Survey Flow

Design and generate the adaptive Q&A onboarding survey for Qasyp App. The survey collects structured business profile data from buyers and suppliers. All output must align with the canonical profile schema in `.claude/context/profile-schema.md`.

## When to Use

- Designing or modifying survey question flows
- Generating survey configuration files (JSON/YAML)
- Validating that survey questions collect all required profile fields
- Adding conditional branching logic (e.g. VAT certificate only if VAT registered)
- Generating database seed data or test profile fixtures

---

## Core Principle: Survey = Profile Schema

Every survey question maps to a specific field in `profile-schema.md`. No question should collect data that has no corresponding profile field. No required field should be left without a corresponding question.

---

## Question Flow

The survey is split into four sections matching the profile schema:

```
Section 1: Legal & Registration
Section 2: Business Profile
Section 3: Financial & Growth
Section 4: Geographic & Partner Preferences
```

### Section 1 — Legal & Registration

| Step | Field               | Type      | Conditional |
|------|---------------------|-----------|-------------|
| 1.1  | `company_name`      | text      | —           |
| 1.2  | `bin`               | text      | —           |
| 1.3  | `legal_entity_type` | single choice | —       |
| 1.4  | `vat_registered`    | boolean   | —           |
| 1.5  | `vat_certificate_number` | text | only if 1.4 = true |

**BIN validation rule:** Must be exactly 12 digits, numeric only.

**Legal entity choices:**
```
ТОО (LLP)
ИП (Sole Proprietor)
АО (JSC)
ГП (State Enterprise)
Other
```

### Section 2 — Business Profile

| Step | Field                  | Type          | Conditional     |
|------|------------------------|---------------|-----------------|
| 2.1  | `role`                 | single choice | —               |
| 2.2  | `industry_sector`      | single choice + other | —      |
| 2.3  | `business_scope`       | long text     | —               |
| 2.4  | `products_services`    | multi-text    | —               |
| 2.5  | `volume_requirements`  | text          | optional        |
| 2.6  | `frequency`            | single choice | optional        |
| 2.7  | `quality_standards`    | multi-select  | optional        |
| 2.8  | `delivery_requirements`| text          | optional        |

**Role choices:**
```
Buyer (I am looking for suppliers)
Supplier (I am offering products or services)
Both
```

**Industry sector choices:**
```
Construction (Строительство)
Agriculture (Сельское хозяйство)
Manufacturing (Производство)
Logistics & Transport (Логистика и транспорт)
IT & Technology (IT и технологии)
Trade & Retail (Торговля)
Oil & Gas (Нефть и газ)
Finance (Финансы)
Healthcare & Pharma (Медицина и фармацевтика)
Education (Образование)
Other
```

**Frequency choices:**
```
ONE_TIME
WEEKLY
MONTHLY
QUARTERLY
ANNUAL
```

**Quality standards (multi-select):**
```
ISO 9001
ISO 14001
HACCP
GOST
Halal
None / Not applicable
Other
```

### Section 3 — Financial & Growth

| Step | Field                  | Type          | Conditional |
|------|------------------------|---------------|-------------|
| 3.1  | `annual_revenue_range` | single choice | optional    |
| 3.2  | `growth_target`        | long text     | optional    |

**Revenue range choices (KZT):**
```
Below 10 million ₸
10 – 50 million ₸
50 – 200 million ₸
200 million – 1 billion ₸
Above 1 billion ₸
Prefer not to say
```

### Section 4 — Geographic & Partner Preferences

| Step | Field                      | Type        | Conditional |
|------|----------------------------|-------------|-------------|
| 4.1  | `operating_regions`        | multi-select | —          |
| 4.2  | `willing_cross_border`     | boolean     | —           |
| 4.3  | `preferred_partner_profile`| long text   | optional    |
| 4.4  | `exclusion_criteria`       | long text   | optional    |

**Kazakhstan regions (multi-select):**
```
Almaty (city)
Astana (city)
Shymkent (city)
Almaty Region
Akmola
Aktobe
Atyrau
East Kazakhstan
Zhambyl
West Kazakhstan
Karaganda
Kostanay
Kyzylorda
Mangystau
Pavlodar
North Kazakhstan
Turkestan
Abai
Zhetysu
Ulytau
```

---

## Branching Logic

```
IF vat_registered = true   → show vat_certificate_number question
IF vat_registered = false  → skip vat_certificate_number

IF role = BUYER            → label products_services as "What do you need to procure?"
IF role = SUPPLIER         → label products_services as "What do you offer?"
IF role = BOTH             → ask separately for buyer needs and supplier offerings
```

---

## Survey Config Format (JSON)

Use this schema when generating survey configuration files:

```json
{
  "survey_id": "onboarding-v1",
  "sections": [
    {
      "id": "legal",
      "title_kk": "...",
      "title_ru": "Юридическая информация",
      "title_en": "Legal & Registration",
      "questions": [
        {
          "id": "company_name",
          "field": "company_name",
          "type": "text",
          "required": true,
          "label_kk": "...",
          "label_ru": "Название компании",
          "label_en": "Company name",
          "validation": {
            "max_length": 255
          }
        },
        {
          "id": "bin",
          "field": "bin",
          "type": "text",
          "required": true,
          "label_kk": "...",
          "label_ru": "БИН",
          "label_en": "Business Identification Number (BIN)",
          "validation": {
            "pattern": "^[0-9]{12}$",
            "error_ru": "БИН должен состоять из 12 цифр",
            "error_en": "BIN must be exactly 12 digits"
          }
        }
      ]
    }
  ]
}
```

---

## Validation Rules

| Field                     | Rule                                                       |
|---------------------------|------------------------------------------------------------|
| `bin`                     | Exactly 12 numeric digits                                  |
| `company_name`            | 1–255 characters, not blank                                |
| `vat_certificate_number`  | Required if `vat_registered = true`                       |
| `products_services`       | At least 1 entry required                                  |
| `operating_regions`       | At least 1 region required                                 |
| `business_scope`          | 20–1000 characters                                         |
| `annual_revenue_range`    | Must match one of the defined enum values                  |

---

## Survey Completion Target

Per the quality attributes in CLAUDE.md: **survey completion rate > 70%**.

Design principles to support this:
- Mark only genuinely required fields as required — financial and partner preference fields are optional
- Keep each section to 4–6 questions maximum
- Show a progress indicator at the top of each section
- Allow saving and resuming the survey at any point
- Provide examples inline for complex fields (e.g. `business_scope`, `quality_standards`)

---

## Checklist

When generating or modifying a survey flow:

- [ ] Every question maps to a named field in `profile-schema.md`
- [ ] All required fields from the schema have a corresponding required question
- [ ] BIN validation pattern is applied (`^[0-9]{12}$`)
- [ ] VAT certificate question is conditional on VAT registered = true
- [ ] All questions have labels in Kazakh, Russian, and English
- [ ] Products/services label changes based on role
- [ ] Region list matches the enum values in `profile-schema.md`
- [ ] Revenue range labels match the KZT brackets in the schema
