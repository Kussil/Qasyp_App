import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.profile import BusinessProfile
from app.services import matching_service, explanation_service
from app.schemas.match import MatchListResponse, MatchResult
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/matches", tags=["matches"])

FREE_TIER_LIMIT = 5


@router.get("", response_model=MatchListResponse)
async def get_matches(
    limit: int = Query(default=20, le=50),
    offset: int = Query(default=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(BusinessProfile).where(BusinessProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Complete your profile survey first")

    # Check cache
    cached = await matching_service.get_cached_matches(str(current_user.id))
    if cached:
        matches_data = cached.get("matches", [])
        total = cached.get("total", len(matches_data))
    else:
        matches_data = await matching_service.search_matches(profile, limit=max(limit, 20), offset=0)
        total = len(matches_data)
        await matching_service.set_cached_matches(
            str(current_user.id), {"matches": matches_data, "total": total}
        )

    # Generate explanations for unlocked matches
    for match in matches_data[:FREE_TIER_LIMIT]:
        if not match.get("explanation"):
            try:
                match["explanation"] = await explanation_service.generate_explanation(profile, match)
            except Exception as e:
                logger.warning(f"Explanation failed: {e}")
                match["explanation"] = None

    # Apply tier gating
    is_free = current_user.tier == "free"
    result_matches = []
    for i, match in enumerate(matches_data[offset:offset + limit]):
        real_index = offset + i
        if is_free and real_index >= FREE_TIER_LIMIT:
            result_matches.append(MatchResult(
                profile_id=None,
                company_name="***",
                match_score=None,
                locked=True,
            ))
        else:
            result_matches.append(MatchResult(**match))

    has_more = (total > offset + limit) or (is_free and total > FREE_TIER_LIMIT)
    return MatchListResponse(matches=result_matches, total=total, has_more=has_more)
