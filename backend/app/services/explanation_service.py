import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

EXPLANATION_CACHE_TTL = 86400  # 24 hours


def _make_fallback_explanation(user_profile, match_data: dict) -> str:
    industry = match_data.get("industry_sector", "the same industry")
    regions = ", ".join(match_data.get("operating_regions", [])[:2]) or "Kazakhstan"
    comp_role = "buyer" if (user_profile.role or "").upper() == "SUPPLIER" else "supplier"
    return f"Matched on {industry} in {regions} with complementary {comp_role} profile."


async def generate_explanation(user_profile, match_data: dict) -> str:
    """Generate LLM explanation for a match. Falls back to template on failure."""
    cache_key = f"explanation:{user_profile.id}:{match_data.get('profile_id')}"

    # Try Redis cache first
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL)
        cached = await r.get(cache_key)
        await r.aclose()
        if cached:
            return cached.decode()
    except Exception:
        pass

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        prompt = f"""You are a B2B matching assistant. Given two business profiles, explain in 1-2 sentences why they are a good match. Reference specific details. Do not fabricate information.

User profile: industry={user_profile.industry_sector}, scope={user_profile.business_scope[:100] if user_profile.business_scope else ''}, role={user_profile.role}
Match profile: industry={match_data.get('industry_sector')}, company={match_data.get('company_name')}, score={match_data.get('match_score')}

Explanation:"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        explanation = message.content[0].text.strip()
        logger.info(f"LLM explanation generated, input_tokens={message.usage.input_tokens}, output_tokens={message.usage.output_tokens}")

        # Cache the explanation
        try:
            import redis.asyncio as aioredis
            r = aioredis.from_url(settings.REDIS_URL)
            await r.setex(cache_key, EXPLANATION_CACHE_TTL, explanation)
            await r.aclose()
        except Exception:
            pass

        return explanation
    except Exception as e:
        logger.warning(f"LLM explanation failed, using fallback: {e}")
        return _make_fallback_explanation(user_profile, match_data)
