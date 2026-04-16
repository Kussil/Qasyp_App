from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services import survey_service
from app.schemas.profile import ProfileCreate, ProfileResponse
from typing import Optional

router = APIRouter(prefix="/survey", tags=["survey"])


@router.get("/questions")
async def get_questions(
    role: Optional[str] = Query(default="buyer"),
    current_user: User = Depends(get_current_user),
):
    """Return survey sections and questions filtered by role (buyer or supplier)."""
    role = role.lower() if role else (current_user.role or "buyer")
    return {"sections": survey_service.get_questions_for_role(role)}


@router.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_survey(
    data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit the onboarding survey and create a business profile."""
    profile = await survey_service.create_profile(current_user, data.model_dump(exclude_none=False), db)
    return {"profile_id": str(profile.id), "status": "completed"}


@router.patch("", response_model=ProfileResponse)
async def update_survey(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Partially update an existing business profile; triggers re-embedding."""
    return await survey_service.update_profile(current_user, data, db)
