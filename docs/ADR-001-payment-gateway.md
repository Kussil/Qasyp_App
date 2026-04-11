# ADR-001: Payment Gateway Selection

**Date:** 2026-04-05
**Status:** `PROPOSED`
**Deciders:** Product + Commercial team
**Epic(s) affected:** E4 (Freemium & Paywall)

---

## Context

Qasyp App needs a payment gateway to process subscriptions (Basic and Pro tiers). The primary market is Kazakhstan. The gateway must support local payment methods familiar to SME users, and must comply with Kazakhstani financial regulations.

---

## Decision Drivers

- Kazakhstan-based SMEs primarily use Kaspi Pay and Halyk Bank for digital payments
- Stripe has limited local support and requires USD settlement, adding FX friction
- Data residency requirements may affect which processors can be used
- Subscription billing (recurring) support is required for Pro tier
- Legal entity type (ТОО / ИП) may affect invoicing requirements

---

## Options Considered

### Option A: Kaspi Pay
**Description:** Kazakhstan's dominant digital payment platform with wide SME adoption.
**Pros:**
- Extremely high adoption rate among Kazakhstani businesses and individuals
- Native KZT settlement
- Strong brand trust locally
**Cons:**
- API maturity and documentation quality lower than international alternatives
- Recurring/subscription billing support needs verification
- May require local legal entity registration
**Cost / Effort:** Medium

### Option B: Halyk Bank API (Halyk Pos)
**Description:** Payment integration via Halyk Bank, the largest bank in Kazakhstan.
**Pros:**
- Strong B2B credibility and legal compliance
- KZT settlement, invoice support
- Established relationships with Kazakhstani legal entities
**Cons:**
- Integration complexity higher than consumer-focused solutions
- Developer documentation in Russian only
**Cost / Effort:** Medium–High

### Option C: Stripe (international)
**Description:** Global payment processor with subscription billing support.
**Pros:**
- Excellent developer experience and documentation
- Robust subscription/recurring billing
- Fast to integrate
**Cons:**
- Limited local payment method support (no Kaspi, no Halyk)
- USD settlement adds FX risk and friction for KZT-based customers
- May not satisfy data residency requirements
**Cost / Effort:** Low (integration) / High (adoption friction)

---

## Decision

**Chosen option:** _TBD — pending commercial team review_

**Rationale:** _To be completed once commercial and legal teams confirm requirements._

---

## Consequences

**Actions required:**
- [ ] Commercial team to confirm KZT settlement requirement
- [ ] Legal team to confirm data residency constraints on payment processing
- [ ] Tech lead to evaluate Kaspi Pay API for recurring billing support
- [ ] Decide on dual-gateway strategy (Kaspi for local, Stripe for international)
