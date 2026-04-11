# ADR-003: Embedding Model Selection

**Date:** 2026-04-05
**Status:** `PROPOSED`
**Deciders:** Tech Lead / AI Lead
**Epic(s) affected:** E3 (Matching Engine / RAG)

---

## Context

Qasyp App's matching engine semantically embeds business profiles for vector similarity search. Profiles contain text in Kazakh, Russian, and English. A multilingual embedding model is mandatory. Model choice affects match quality, latency, re-indexing cost, and vendor dependency.

---

## Decision Drivers

- Must support Kazakh language (low-resource language — not all models cover it well)
- Must support Russian (widely used in Kazakhstani B2B context)
- Embedding quality directly determines match precision (target: >80% user satisfaction)
- Model changes require full re-indexing of the vector DB — costly at scale
- API latency must support <2s total match query response time
- On-premise or self-hosted option preferred for data privacy

---

## Options Considered

### Option A: `multilingual-e5-large` (Microsoft / HuggingFace)
**Description:** Open-source multilingual model supporting 100+ languages including Russian and Kazakh.
**Pros:**
- Strong multilingual performance including Russian
- Self-hostable — no third-party data exposure
- Free to use
**Cons:**
- Kazakh language coverage is limited (low-resource)
- Requires GPU infrastructure for reasonable latency
**Cost / Effort:** Medium (self-hosting setup)

### Option B: OpenAI `text-embedding-3-large`
**Description:** OpenAI's flagship embedding model.
**Pros:**
- Strong multilingual performance
- Simple API, no infrastructure to manage
- High-dimensional embeddings (3072d) for precision
**Cons:**
- Kazakh coverage unconfirmed — needs benchmarking
- Data sent to OpenAI API (privacy consideration)
- Per-token cost at scale
**Cost / Effort:** Low (integration) / Ongoing API cost

### Option C: Cohere `embed-multilingual-v3.0`
**Description:** Cohere's multilingual embedding model.
**Pros:**
- Designed for multilingual retrieval use cases
- Good Russian support; Kazakh needs benchmarking
- Compression options reduce storage cost
**Cons:**
- Data sent to Cohere API
- Less widely adopted than OpenAI in the ecosystem
**Cost / Effort:** Low–Medium

### Option D: Custom fine-tuned model on KZ business corpus
**Description:** Fine-tune an existing multilingual model on Kazakhstani business profile data.
**Pros:**
- Best possible domain and language fit
- Full control over quality
**Cons:**
- Requires labelled training data (not yet available)
- Significant time and cost investment
- Not viable for initial launch
**Cost / Effort:** Very High

---

## Decision

**Chosen option:** _TBD — benchmark Options A, B, C on a sample of KZ business profiles before deciding_

---

## Consequences

**Actions required:**
- [ ] Build a benchmark dataset of 50–100 sample KZ business profiles (Kazakh + Russian)
- [ ] Run embedding quality tests (semantic similarity, retrieval precision) across options A, B, C
- [ ] Confirm Kazakh language token coverage for each model
- [ ] Decide on self-hosted vs. API-based approach based on data residency ADR-002 outcome
- [ ] Document chosen `embedding_model_version` — any future change triggers full re-index
