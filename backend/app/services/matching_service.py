import json
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.profile import BusinessProfile
from app.core.config import settings

logger = logging.getLogger(__name__)

COMPLEMENTARY_ROLE = {"BUYER": "SUPPLIER", "SUPPLIER": "BUYER", "buyer": "supplier", "supplier": "buyer"}
CACHE_TTL = 3600  # 1 hour


def build_qdrant_filter(user_profile) -> dict:
    """Build Qdrant filter conditions for hard filtering."""
    complementary = COMPLEMENTARY_ROLE.get(user_profile.role, "SUPPLIER")
    must = [
        {"key": "role", "match": {"value": complementary}}
    ]
    # Region filter: skip if cross-border willing
    if not user_profile.willing_cross_border:
        user_regions = user_profile.operating_regions or []
        if user_regions:
            should = [
                {"key": "operating_regions", "match": {"any": user_regions}},
                {"key": "willing_cross_border", "match": {"value": True}},
            ]
            return {"must": must, "should": should}
    return {"must": must}


async def get_cached_matches(user_id: str) -> Optional[dict]:
    """Try to get cached matches from Redis."""
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL)
        cached = await r.get(f"matches:{user_id}")
        await r.aclose()
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Redis cache miss or error: {e}")
    return None


async def set_cached_matches(user_id: str, data: dict) -> None:
    """Cache match results in Redis."""
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL)
        await r.setex(f"matches:{user_id}", CACHE_TTL, json.dumps(data))
        await r.aclose()
    except Exception as e:
        logger.warning(f"Failed to cache matches: {e}")


async def search_matches(user_profile, limit: int = 20, offset: int = 0) -> List[dict]:
    """Search Qdrant for matching profiles."""
    from app.services.embedding_service import build_embedding_text, get_embedding

    text = build_embedding_text(user_profile)
    vector = get_embedding(text)
    if not vector:
        logger.warning("Empty embedding vector, returning empty matches")
        return []

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny

        client = QdrantClient(url=settings.QDRANT_URL)
        qdrant_filter = build_qdrant_filter(user_profile)

        # Build filter object
        must_conditions = []
        for cond in qdrant_filter.get("must", []):
            must_conditions.append(FieldCondition(key=cond["key"], match=MatchValue(value=cond["match"]["value"])))

        should_conditions = []
        for cond in qdrant_filter.get("should", []):
            if "any" in cond["match"]:
                should_conditions.append(FieldCondition(key=cond["key"], match=MatchAny(any=cond["match"]["any"])))
            else:
                should_conditions.append(FieldCondition(key=cond["key"], match=MatchValue(value=cond["match"]["value"])))

        filter_obj = Filter(must=must_conditions, should=should_conditions if should_conditions else None)

        results = client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=vector,
            query_filter=filter_obj,
            limit=limit + offset,
            with_payload=True,
        )

        matches = []
        for hit in results[offset:offset + limit]:
            payload = hit.payload or {}
            if str(payload.get("profile_id")) != str(user_profile.id):
                matches.append({
                    "profile_id": payload.get("profile_id"),
                    "company_name": payload.get("company_name", "Unknown"),
                    "industry_sector": payload.get("industry_sector"),
                    "operating_regions": payload.get("operating_regions", []),
                    "match_score": round(hit.score, 4),
                    "locked": False,
                })
        return matches
    except Exception as e:
        logger.error(f"Qdrant search failed: {e}")
        return []
