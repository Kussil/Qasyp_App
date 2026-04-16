"""
Dependency injection helpers for FastAPI endpoints.
get_current_user is implemented here as a stub; E1 subagent provides the full JWT implementation.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validate Bearer token and return the authenticated User.
    Full JWT verification is implemented by the E1 (Auth) subagent.
    This stub raises 403 when no credentials are supplied, matching the integration test expectations.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated",
        )
    # E1 will replace this with actual JWT decoding and user lookup.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Auth not yet implemented — awaiting E1 subagent",
    )
