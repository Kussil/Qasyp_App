---
name: rag-pipeline
description: Generate and review RAG pipeline code for Qasyp App's matching engine (E3). Use when writing embedding pipelines, vector store operations, match query logic, or retrieval scoring. Encodes Qdrant/pgvector patterns, hard filter logic, and embedding model versioning requirements.
---

# RAG Pipeline

Code patterns and conventions for Qasyp App's matching engine — the embedding pipeline, vector store operations, pre-retrieval filtering, and match scoring.

## When to Use

- Writing or reviewing the embedding pipeline
- Building vector store insert, query, or re-index operations
- Implementing the match filter logic (role, region, revenue)
- Adding or changing the match scoring or ranking output
- Changing the embedding model (triggers re-index requirement)

---

## Architecture Overview

```
Business Profile (PostgreSQL)
        │
        ▼
Embedding Pipeline (Celery task)
        │  generates vector from text fields
        ▼
Vector Store (Qdrant or pgvector)
        │  stores vector + metadata payload
        ▼
Match Query
   1. Apply hard filters (role, region, VAT)   ← pre-retrieval
   2. Vector similarity search                  ← retrieval
   3. Re-rank and score                         ← post-retrieval
        │
        ▼
Ranked Match Results
```

---

## Fields Embedded (text concatenation)

```python
def build_embedding_text(profile: BusinessProfile) -> str:
    """
    Concatenate embeddable fields into a single string for vectorisation.
    Order matters — keep consistent across all profiles.
    """
    parts = [
        profile.business_scope or "",
        " ".join(profile.products_services or []),
        profile.industry_sector or "",
        " ".join(profile.quality_standards or []),
        profile.preferred_partner_profile or "",
        profile.growth_target or "",
    ]
    return " ".join(filter(None, parts))
```

**Fields that are NOT embedded** (used as hard filter metadata only):
- `bin`, `legal_entity_type`, `vat_registered`
- `role` (BUYER / SUPPLIER / BOTH)
- `operating_regions`
- `annual_revenue_range`
- `willing_cross_border`

---

## Embedding Model Versioning (mandatory)

Every record in the vector store must carry the embedding model version in its metadata payload. A model change requires a full re-index.

```python
EMBEDDING_MODEL_VERSION = "multilingual-e5-large-v1"  # update on model change

def get_embedding_payload(profile: BusinessProfile, vector: list[float]) -> dict:
    return {
        "profile_id": str(profile.id),
        "role": profile.role.value,
        "operating_regions": [r.value for r in profile.operating_regions],
        "willing_cross_border": profile.willing_cross_border,
        "annual_revenue_range": profile.annual_revenue_range.value if profile.annual_revenue_range else None,
        "vat_registered": profile.vat_registered,
        "embedding_model_version": EMBEDDING_MODEL_VERSION,
        "indexed_at": datetime.utcnow().isoformat(),
    }
```

---

## Qdrant Patterns

### Collection Setup

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

client = QdrantClient(url=settings.QDRANT_URL)

client.recreate_collection(
    collection_name="business_profiles",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
)

# Create payload indexes for hard filter fields
client.create_payload_index("business_profiles", "role", PayloadSchemaType.KEYWORD)
client.create_payload_index("business_profiles", "operating_regions", PayloadSchemaType.KEYWORD)
client.create_payload_index("business_profiles", "willing_cross_border", PayloadSchemaType.BOOL)
client.create_payload_index("business_profiles", "embedding_model_version", PayloadSchemaType.KEYWORD)
```

### Upsert a Profile

```python
from qdrant_client.models import PointStruct

async def upsert_profile_embedding(
    profile: BusinessProfile,
    vector: list[float],
    client: QdrantClient,
) -> None:
    """Insert or update a profile's vector in Qdrant."""
    point = PointStruct(
        id=str(profile.id),
        vector=vector,
        payload=get_embedding_payload(profile, vector),
    )
    client.upsert(collection_name="business_profiles", points=[point])
```

### Match Query with Hard Filters

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny

def build_match_filter(
    query_profile: BusinessProfile,
    model_version: str,
) -> Filter:
    """
    Build pre-retrieval hard filters.
    Role must be complementary. Regions must overlap unless cross-border is allowed.
    """
    # Determine target role
    if query_profile.role == Role.BUYER:
        target_roles = [Role.SUPPLIER.value, Role.BOTH.value]
    elif query_profile.role == Role.SUPPLIER:
        target_roles = [Role.BUYER.value, Role.BOTH.value]
    else:
        target_roles = [Role.BUYER.value, Role.SUPPLIER.value, Role.BOTH.value]

    must_conditions = [
        FieldCondition(key="role", match=MatchAny(any=target_roles)),
        FieldCondition(key="embedding_model_version", match=MatchValue(value=model_version)),
    ]

    # Region filter — skip if the querying profile is open to cross-border
    if not query_profile.willing_cross_border:
        region_values = [r.value for r in query_profile.operating_regions]
        must_conditions.append(
            FieldCondition(key="operating_regions", match=MatchAny(any=region_values))
        )

    return Filter(must=must_conditions)


async def search_matches(
    query_profile: BusinessProfile,
    query_vector: list[float],
    client: QdrantClient,
    limit: int = 20,
) -> list[dict]:
    """
    Run semantic match search with pre-retrieval hard filters.
    Returns up to `limit` results ranked by cosine similarity.
    """
    results = client.search(
        collection_name="business_profiles",
        query_vector=query_vector,
        query_filter=build_match_filter(query_profile, EMBEDDING_MODEL_VERSION),
        limit=limit,
        with_payload=True,
    )
    return [{"profile_id": r.id, "score": r.score, "payload": r.payload} for r in results]
```

---

## pgvector Patterns (alternative)

If using pgvector instead of Qdrant:

```python
# SQLAlchemy model with vector column
from pgvector.sqlalchemy import Vector

class ProfileEmbedding(Base):
    __tablename__ = "profile_embeddings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    profile_id: Mapped[UUID] = mapped_column(ForeignKey("business_profiles.id"), unique=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(1024))
    embedding_model_version: Mapped[str] = mapped_column(String(64))
    indexed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# Similarity query with hard filters
async def search_matches_pgvector(
    query_profile: BusinessProfile,
    query_vector: list[float],
    session: AsyncSession,
    limit: int = 20,
) -> list[ProfileEmbedding]:
    stmt = (
        select(ProfileEmbedding)
        .join(BusinessProfile, ProfileEmbedding.profile_id == BusinessProfile.id)
        .where(
            BusinessProfile.role.in_(target_roles),
            ProfileEmbedding.embedding_model_version == EMBEDDING_MODEL_VERSION,
        )
        .order_by(ProfileEmbedding.embedding.cosine_distance(query_vector))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()
```

---

## Celery Embedding Task

```python
from app.tasks.celery_app import celery
from app.services.embedding import embed_text
from app.services.vector_store import upsert_profile_embedding

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def index_profile_embedding(self, profile_id: str) -> None:
    """
    Async task: generate and store embedding for a business profile.
    Triggered after profile creation or update.
    """
    try:
        profile = BusinessProfile.get(profile_id)
        text = build_embedding_text(profile)
        vector = embed_text(text)
        upsert_profile_embedding(profile, vector)
    except Exception as exc:
        raise self.retry(exc=exc)
```

---

## Re-indexing Rule

**Any change to the embedding model requires a full re-index of all profiles.**

Steps:
1. Update `EMBEDDING_MODEL_VERSION` constant
2. Write a migration script at `scripts/reindex_embeddings.py`
3. Run the script before deploying the new model version
4. Commit message must include: `BREAKING CHANGE: full profile re-index required`

---

## Checklist

Before merging any RAG pipeline change:

- [ ] `EMBEDDING_MODEL_VERSION` is set and matches the model in use
- [ ] All vector store writes include the version in the payload
- [ ] Hard filters are applied before vector similarity search, not after
- [ ] Role complementarity logic is correct (BOTH ↔ BUYER or SUPPLIER)
- [ ] Region filter is skipped when `willing_cross_border = true`
- [ ] LLM/embedding calls are wrapped in try/except
- [ ] Re-index script provided if model version changed
- [ ] Unit tests cover filter logic and scoring output
