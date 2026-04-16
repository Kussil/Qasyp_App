from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.tier_service import upgrade_to_basic_demo
from app.core.config import settings

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/upgrade")
async def demo_upgrade(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mock upgrade to basic tier — only available in DEMO_MODE."""
    return await upgrade_to_basic_demo(current_user, db)
