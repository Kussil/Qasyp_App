import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.profile import BusinessProfile


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tier: Mapped[str] = mapped_column(String(20), default="free", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    profile_submitted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    profile: Mapped[Optional["BusinessProfile"]] = relationship(
        "BusinessProfile", back_populates="user", uselist=False
    )
