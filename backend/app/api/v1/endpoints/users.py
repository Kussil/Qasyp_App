from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, RoleUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me/role", response_model=UserResponse)
async def set_role(
    request: RoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    role = request.role.lower()
    if role not in ("buyer", "supplier"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Role must be 'buyer' or 'supplier'")
    if current_user.profile_submitted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role is locked after survey submission")

    current_user.role = role
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
