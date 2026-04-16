import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


async def upgrade_to_basic_demo(user: User, db: AsyncSession) -> dict:
    """Upgrade user to basic tier (demo mode only)."""
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    user.tier = "basic"
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info(f"Demo upgrade: user {user.id} upgraded to basic")
    return {"tier": "basic", "message": "Upgraded (demo mode)"}
