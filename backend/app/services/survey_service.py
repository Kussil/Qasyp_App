import json
import re
import logging
from pathlib import Path
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.profile import BusinessProfile
from app.models.user import User

logger = logging.getLogger(__name__)

SURVEY_CONFIG_PATH = Path(__file__).parent.parent / "data" / "survey_config.json"
_config_cache = None


def load_survey_config() -> dict:
    """Load and cache the survey configuration from JSON."""
    global _config_cache
    if _config_cache is None:
        with open(SURVEY_CONFIG_PATH) as f:
            _config_cache = json.load(f)
    return _config_cache


def get_questions_for_role(role: str) -> list:
    """Return survey sections filtered to questions relevant for the given role."""
    config = load_survey_config()
    sections = []
    for section in config["sections"]:
        filtered_questions = [
            q for q in section["questions"]
            if role in q.get("roles", [role])
        ]
        if filtered_questions:
            sections.append({**section, "questions": filtered_questions})
    return sections


def validate_bin(bin_value: str) -> bool:
    """Validate that BIN is exactly 12 numeric digits."""
    return bool(re.match(r"^[0-9]{12}$", bin_value))


def validate_profile_data(data: dict, role: str) -> None:
    """Validate required fields and business rules for profile submission."""
    required_fields = ["company_name", "bin", "legal_entity_type", "vat_registered",
                       "industry_sector", "business_scope", "products_services", "operating_regions"]
    for field in required_fields:
        if field not in data or data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Field '{field}' is required"
            )
    if not validate_bin(str(data.get("bin", ""))):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="BIN must be exactly 12 digits"
        )
    if data.get("vat_registered") and not data.get("vat_certificate_number"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="VAT certificate number is required when VAT registered"
        )


async def create_profile(user: User, data: dict, db: AsyncSession) -> BusinessProfile:
    """Create a new business profile for the user and dispatch embedding generation."""
    existing = await db.execute(select(BusinessProfile).where(BusinessProfile.user_id == user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile already submitted")

    validate_profile_data(data, user.role or "buyer")

    profile = BusinessProfile(
        user_id=user.id,
        role=(user.role or "buyer").upper(),
        **{k: v for k, v in data.items() if k != "role"},
    )
    db.add(profile)
    user.profile_submitted = True
    db.add(user)
    await db.commit()
    await db.refresh(profile)

    # Dispatch embedding task (non-blocking); E3 implements the actual logic
    try:
        from app.tasks.embedding_tasks import generate_embedding
        generate_embedding.delay(str(profile.id))
    except Exception as e:
        logger.warning(f"Could not dispatch embedding task: {e}")

    return profile


async def update_profile(user: User, data: dict, db: AsyncSession) -> BusinessProfile:
    """Partially update an existing business profile and trigger re-embedding."""
    result = await db.execute(select(BusinessProfile).where(BusinessProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    for key, value in data.items():
        if hasattr(profile, key) and value is not None:
            setattr(profile, key, value)

    profile.embedding_generated = False
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    try:
        from app.tasks.embedding_tasks import generate_embedding
        generate_embedding.delay(str(profile.id))
    except Exception as e:
        logger.warning(f"Could not dispatch re-embedding task: {e}")

    return profile
