# CLAUDE.md — Qasyp App

> This file provides context for AI assistants (and team members) working in this repository.
> It follows the Agile/Scrum framing standard and ISO 25010 quality model conventions.

---

## 1. Project Overview

**Project Name:** Qasyp App
**Type:** B2B SaaS Platform with AI/ML and Agentic capabilities
**Stage:** Greenfield — active development
**Primary Market:** Kazakhstan (regional B2B ecosystem)
**Language / Locale:** Kazakh, Russian (primary); English (secondary)

### Vision

Qasyp App is an AI-powered B2B matchmaking platform that connects businesses in Kazakhstan by intelligently pairing customers with suppliers based on their operational needs, product/service profiles, and growth potential.

### Mission

To reduce the friction of B2B discovery in the Kazakhstani market by replacing manual sourcing and cold outreach with a structured, data-driven matching engine and autonomous AI agents that negotiate and gather offers on behalf of platform users.

---

## 2. Core Problem Statement

Businesses in Kazakhstan — particularly SMEs — spend disproportionate time and resources finding reliable suppliers or customers. Existing channels (word of mouth, trade directories, marketplaces) are fragmented, unstructured, and manual. Qasyp App solves this by:

1. Structuring business profiles through guided Q&A onboarding.
2. Using AI/RAG to semantically match businesses based on real needs.
3. Deploying autonomous AI agents to proactively outreach and negotiate on behalf of Pro users.

---

## 3. Product Pillars

### Pillar 1 — Structured Onboarding (Survey Engine)
Collects key business profile data from both **customers** (buyers) and **suppliers** (providers) via an adaptive Q&A survey. Fields include:

**Legal & Registration**
- Company name and BIN (Business Identification Number)
- Legal entity type: ТОО (LLP), ИП (Sole Proprietor), АО (JSC), ГП (State Enterprise), or other
- VAT status: VAT registered (НДС плательщик) or non-VAT registered (без НДС), including VAT certificate number where applicable

**Business Profile**
- Industry sector and business scope
- Products/services offered or required
- Volume, frequency, quality standards, and delivery requirements

**Financial & Growth**
- Current business revenue range (annual turnover bracket)
- Growth potential and expansion targets

**Geographic & Partner Preferences**
- Operating regions within Kazakhstan (oblast / city)
- Willingness to work with counterparties outside Kazakhstan
- Preferred partner profile and any exclusion criteria

### Pillar 2 — AI-Powered Matching Engine (RAG Core)
- Ingests structured survey responses into a vector database (e.g., Qdrant, Weaviate, or pgvector)
- Matches businesses semantically using Retrieval-Augmented Generation (RAG)
- Returns a ranked **shortlist** of compatible partners (free tier: top 3–5 results shown)
- Full list is gated behind a paid subscription or one-time unlock (commercial model TBD)

### Pillar 3 — AI Agent Outreach (Pro Subscription Feature)
- Activated once a Pro Subsription user selects a full partner list
- Autonomous agents act as business development specialists
- Per matched partner, an agent initiates contact (email/chat), introduces the user's business, probes for interest, and may negotiate terms or request offers
- User receives consolidated updates and summaries from each agent interaction
- Agent persona: professional, sector-aware, respectful of local business culture

---

## 4. Commercial Model

| Tier       | Features                                                             | Pricing Model         |
|------------|----------------------------------------------------------------------|-----------------------|
| Free       | Survey onboarding, shortlist preview (top 3–5 matches)              | Free                  |
| Basic      | Full matched partner list                                            | Subscription or one-time (TBD) |
| Pro        | Full list + AI Agent outreach, negotiation, offer collection         | Premium subscription  |

> **Note:** Exact pricing tiers, billing cycles, and regional payment integrations (Kaspi, Halyk) are subject to product and commercial team review.

---

## 5. Technical Architecture

### Stack

| Layer              | Technology                                      |
|--------------------|--------------------------------------------------|
| Backend API        | Python — FastAPI (preferred) or Django REST Framework |
| AI / LLM Layer     | LangChain / LlamaIndex + Anthropic Claude API or OpenAI |
| Vector Database    | Qdrant / pgvector (PostgreSQL extension)         |
| Relational DB      | PostgreSQL                                       |
| Task Queue         | Celery + Redis                                   |
| Agent Orchestration| LangGraph or CrewAI                              |
| Frontend           | React / Next.js (TypeScript)                     |
| Auth               | JWT + OAuth2 (Google, email-link)                |
| Cloud              | AWS or GCP (Kazakhstan-compliant data residency preferred) |
| CI/CD              | GitHub Actions                                   |
| Containerization   | Docker + Docker Compose (dev); Kubernetes (prod) |

### High-Level System Design

```
[User / Business]
      │
      ▼
[Survey Engine] ──── structured profile ────► [Profile Store (PostgreSQL)]
                                                        │
                                              [Embedding Pipeline]
                                                        │
                                                        ▼
                                              [Vector DB (Qdrant / pgvector)]
                                                        │
                                              [RAG Matching Engine]
                                                        │
                                   ┌────────────────────┴────────────────────┐
                                   ▼                                         ▼
                          [Free Shortlist]                        [Full List — Paid]
                                                                             │
                                                                  [AI Agent Orchestrator]
                                                                             │
                                                             ┌───────────────┴──────────────┐
                                                             ▼                              ▼
                                                   [Email Agent]               [Chat/Message Agent]
                                                             │                              │
                                                             └────────────────┬─────────────┘
                                                                              ▼
                                                                  [User Dashboard — Updates & Offers]
```

---

## 6. Agile / Scrum Structure

### Epics

| ID  | Epic Name                     | Description                                                      |
|-----|-------------------------------|------------------------------------------------------------------|
| E1  | User Onboarding & Auth        | Registration, login, role selection (buyer/supplier), profile setup |
| E2  | Survey Engine                 | Adaptive Q&A flow, data validation, profile storage              |
| E3  | Matching Engine (RAG)         | Embedding pipeline, vector search, match ranking                 |
| E4  | Freemium & Paywall            | Shortlist gate, subscription/payment integration                 |
| E5  | AI Agent Outreach             | Agent orchestration, outreach logic, status tracking             |
| E6  | User Dashboard                | Match results, agent updates, offer management                   |
| E7  | Admin & Analytics             | Platform monitoring, user management, KPI dashboards             |

### Sprint Cadence

- Sprint length: **2 weeks**
- Ceremonies: Planning, Daily Standup, Review, Retrospective
- Backlog managed in: [tool TBD — Jira / Linear / GitHub Projects]
- Definition of Done: Code reviewed, tested (unit + integration), deployed to staging, acceptance criteria met

---

## 7. Key User Roles

| Role         | Description                                                             |
|--------------|-------------------------------------------------------------------------|
| Buyer        | A business seeking products or services from suppliers                  |
| Supplier     | A business offering products or services to buyers                      |
| Pro User     | A Buyer or Supplier on the paid tier with access to Agent Outreach      |
| Admin        | Platform operator with access to user management and analytics          |

---

## 8. Data & AI Guidelines

- All business profile data is treated as **confidential commercial information**
- Embeddings are generated server-side; raw profile text is never exposed to third parties
- LLM prompts must be designed to avoid hallucination in business matching context — use structured retrieval, not generation, for match decisions
- AI agents must operate within defined communication boundaries (no financial commitments, no binding agreements)
- Agent tone: professional, concise, representative of the platform user's interest
- All agent-sent messages must be logged and auditable per user account

---

## 9. Quality Attributes (ISO 25010)

| Attribute         | Target Standard                                                      |
|-------------------|----------------------------------------------------------------------|
| Functional Suitability | Matches must be relevant (precision > 80% in user feedback surveys) |
| Performance Efficiency | Match query response < 2s; Agent status update latency < 5min     |
| Usability         | Onboarding survey completion rate > 70%; Mobile-first responsive UI |
| Security          | OWASP Top 10 compliance; encrypted data at rest and in transit       |
| Reliability       | 99.5% uptime SLA (production); graceful degradation on AI failures   |
| Maintainability   | Modular services; >70% unit test coverage; documented APIs           |
| Portability       | Docker-containerized; cloud-agnostic where possible                  |

---

## 10. Conventions for AI Assistants Working in This Repo

- **Language:** All code comments and docstrings in **English**. UI copy in **Kazakh/Russian** (managed via i18n files).
- **Code style:** PEP 8 (Python), ESLint + Prettier (TypeScript/React)
- **Branching:** `main` (protected), `develop`, `feature/[epic-id]-[short-description]`
- **Commit format:** Conventional Commits — `feat(E2): add adaptive survey branching logic`
- **Environment variables:** Never hardcode secrets. Use `.env` + `python-dotenv` locally; secrets manager in production.
- **AI/LLM calls:** Always wrap in try/except with fallback; log token usage per request.
- **Vector DB operations:** Always version your embedding models — a model change requires re-indexing.
- **Agent actions:** No agent should take irreversible external actions (e.g. send emails) without a human-in-the-loop approval flag in staging.

---

## 11. Open Questions / Decisions Pending

- [ ] Final choice: subscription vs. one-time payment model for Basic tier
- [ ] Payment gateway for Kazakhstan market (Kaspi Pay, Halyk Bank API, Stripe?)
- [ ] Data residency: local Kazakhstani cloud (Kazteleport) vs. AWS Frankfurt with contractual compliance
- [ ] Agent outreach channel: email-first, WhatsApp Business API, or custom in-app messaging
- [ ] Embedding model selection: multilingual model required (Kazakh + Russian + English support)
- [ ] Legal/compliance: personal data handling under Kazakhstan's Law on Personal Data

---

## 12. Glossary

| Term          | Definition                                                              |
|---------------|-------------------------------------------------------------------------|
| RAG           | Retrieval-Augmented Generation — AI technique combining vector search with LLM generation |
| Buyer         | Platform user seeking to procure goods or services                      |
| Supplier      | Platform user offering goods or services                                |
| Shortlist     | A ranked subset of matched partners returned to a free user             |
| Full List     | Complete ranked match results, available to paid users                  |
| Agent         | An autonomous AI entity acting on behalf of a Pro user for outreach     |
| Embedding     | A vector representation of a business profile used for semantic matching |
| Match Score   | A relevance ranking computed by the RAG engine between two profiles     |

---

*Last updated: April 2026 | Maintained by: Qasyp App core team*
