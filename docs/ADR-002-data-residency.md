# ADR-002: Data Residency and Cloud Hosting

**Date:** 2026-04-05
**Status:** `PROPOSED`
**Deciders:** CTO / Tech Lead + Legal team
**Epic(s) affected:** E1, E2, E3, E7

---

## Context

Qasyp App stores confidential commercial data (business profiles, BINs, financial ranges, contact information). Kazakhstan's Law on Personal Data (Закон РК «О персональных данных и их защите») may require that personal data of Kazakhstani citizens be stored on servers located within Kazakhstan. This affects cloud provider selection.

---

## Decision Drivers

- Kazakhstan data localisation law compliance
- Latency for Kazakhstani users (local hosting preferred)
- Availability of managed services (PostgreSQL, Redis, vector DB) in local cloud
- Cost and operational maturity of Kazakhstani cloud providers vs. hyperscalers
- Need for Kubernetes and CI/CD-compatible infrastructure

---

## Options Considered

### Option A: Kazteleport (local Kazakhstani cloud)
**Description:** Government-linked Kazakhstani cloud provider with local data centres.
**Pros:**
- Full compliance with KZ data residency law
- Local latency advantage
- Potential for government contract eligibility
**Cons:**
- Limited managed service offering vs. AWS/GCP
- Smaller engineering community and ecosystem
- Less mature DevOps tooling
**Cost / Effort:** Medium–High

### Option B: AWS Frankfurt (EU) with contractual compliance
**Description:** Host on AWS eu-central-1 with DPA agreements claiming compliance.
**Pros:**
- Full managed service ecosystem (RDS, ElastiCache, EKS)
- Excellent DevOps tooling and CI/CD support
- Team familiarity
**Cons:**
- May not satisfy strict KZ data localisation requirements
- Regulatory risk if law is enforced strictly
- Higher latency from Frankfurt to Kazakhstan
**Cost / Effort:** Low (infrastructure) / High (legal risk)

### Option C: Hybrid — local for personal data, AWS for compute
**Description:** Store personal/business profile data on Kazteleport; use AWS for AI compute, vector DB, and heavy workloads.
**Pros:**
- Balances compliance with operational maturity
- Limits exposure of sensitive data
**Cons:**
- Cross-region data transfer complexity
- Higher architectural overhead
**Cost / Effort:** High

---

## Decision

**Chosen option:** _TBD — pending legal review of KZ data localisation law applicability_

---

## Consequences

**Actions required:**
- [ ] Legal team to determine if KZ data localisation law applies to B2B platform data (BIN, company name) vs. personal data only
- [ ] Evaluate Kazteleport managed PostgreSQL and Redis availability
- [ ] Get infrastructure cost estimates from Kazteleport and AWS Frankfurt
- [ ] Confirm with GDPR/KZ law specialist whether AWS Frankfurt DPA is sufficient
