# Qasyp App — Business Profile Schema

> Canonical reference for the business profile data model.
> Used by the Survey Engine (E2), Matching Engine (E3), and Agent Outreach (E5).
> All fields must align with the survey Q&A flow and the vector embedding pipeline.

---

## Profile Types

Every business on the platform is either a **Buyer** (seeks products/services) or a **Supplier** (offers products/services). A single company may hold both roles.

---

## Field Definitions

### 1. Legal & Registration

| Field              | Type     | Required | Notes                                              |
|--------------------|----------|----------|----------------------------------------------------|
| `company_name`     | string   | Yes      | Official registered name                           |
| `bin`              | string   | Yes      | Business Identification Number (БИН) — 12 digits  |
| `legal_entity_type`| enum     | Yes      | See values below                                   |
| `vat_registered`   | boolean  | Yes      | True = НДС плательщик                              |
| `vat_certificate_number` | string | Conditional | Required if `vat_registered = true`         |

**`legal_entity_type` values:**
- `TOO` — ТОО (Товарищество с Ограниченной Ответственностью / LLP)
- `IP` — ИП (Индивидуальный Предприниматель / Sole Proprietor)
- `AO` — АО (Акционерное Общество / JSC)
- `GP` — ГП (Государственное Предприятие / State Enterprise)
- `OTHER`

---

### 2. Business Profile

| Field                  | Type          | Required | Notes                                         |
|------------------------|---------------|----------|-----------------------------------------------|
| `industry_sector`      | string        | Yes      | Free text + normalized to taxonomy (see below)|
| `business_scope`       | string        | Yes      | Brief description of what the business does   |
| `role`                 | enum          | Yes      | `BUYER`, `SUPPLIER`, or `BOTH`                |
| `products_services`    | list[string]  | Yes      | Items offered (Supplier) or required (Buyer)  |
| `volume_requirements`  | string        | No       | Expected transaction volume (e.g. "5 тонн/месяц") |
| `frequency`            | enum          | No       | `ONE_TIME`, `WEEKLY`, `MONTHLY`, `QUARTERLY`, `ANNUAL` |
| `quality_standards`    | list[string]  | No       | e.g. ISO 9001, GOST, HACCP                   |
| `delivery_requirements`| string        | No       | Delivery terms, incoterms, or custom          |

**Industry Sector Taxonomy (top-level):**
- Строительство (Construction)
- Сельское хозяйство (Agriculture)
- Производство (Manufacturing)
- Логистика и транспорт (Logistics & Transport)
- IT и технологии (IT & Technology)
- Торговля (Trade & Retail)
- Нефть и газ (Oil & Gas)
- Финансы (Finance)
- Медицина и фармацевтика (Healthcare & Pharma)
- Образование (Education)
- Другое (Other)

---

### 3. Financial & Growth

| Field                  | Type   | Required | Notes                                              |
|------------------------|--------|----------|----------------------------------------------------|
| `annual_revenue_range` | enum   | No       | Bracket in KZT (see values below)                 |
| `growth_target`        | string | No       | Narrative: expansion plans, new markets, etc.     |

**`annual_revenue_range` values:**
- `BELOW_10M` — до 10 млн ₸
- `10M_50M` — 10–50 млн ₸
- `50M_200M` — 50–200 млн ₸
- `200M_1B` — 200 млн – 1 млрд ₸
- `ABOVE_1B` — свыше 1 млрд ₸
- `PREFER_NOT_TO_SAY`

---

### 4. Geographic & Partner Preferences

| Field                      | Type         | Required | Notes                                          |
|----------------------------|--------------|----------|------------------------------------------------|
| `operating_regions`        | list[enum]   | Yes      | Kazakhstan oblasts / cities (see below)        |
| `willing_cross_border`     | boolean      | No       | Willing to work with non-KZ counterparties     |
| `preferred_partner_profile`| string       | No       | Narrative description of ideal partner         |
| `exclusion_criteria`       | string       | No       | Types of partners to exclude                   |

**Kazakhstan Region Values:**
```
ALMATY_CITY, ASTANA_CITY, SHYMKENT_CITY,
ALMATY_REGION, AKMOLA, AKTOBE, ATYRAU,
EAST_KZ, ZHAMBYL, WEST_KZ, KARAGANDA,
KOSTANAY, KYZYLORDA, MANGYSTAU, PAVLODAR,
NORTH_KZ, TURKESTAN, ABAI, ZHETYSU, ULYTAU
```

---

## Embedding Strategy

The following fields are concatenated and embedded into the vector store for semantic matching:

```
business_scope + products_services + industry_sector +
quality_standards + preferred_partner_profile + growth_target
```

**Not embedded** (used for hard filters only):
- `bin`, `vat_registered`, `legal_entity_type`
- `operating_regions`, `willing_cross_border`
- `annual_revenue_range`

---

## Match Filter Logic (pre-retrieval)

Before vector similarity search, apply hard filters:
1. `role` must be complementary (Buyer ↔ Supplier)
2. `operating_regions` must overlap (unless `willing_cross_border = true`)
3. Optionally filter by `annual_revenue_range` bracket compatibility

---

## Versioning Note

> If the embedding model changes, **all profiles must be re-indexed**.
> Tag each embedding record with `embedding_model_version` in the vector DB metadata.
