import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Legal & Registration
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    bin: Mapped[str] = mapped_column(String(12), nullable=False)
    legal_entity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    vat_registered: Mapped[bool] = mapped_column(Boolean, nullable=False)
    vat_certificate_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Business Profile
    industry_sector: Mapped[str] = mapped_column(String(100), nullable=False)
    business_scope: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # BUYER, SUPPLIER, BOTH
    products_services: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    volume_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    frequency: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    quality_standards: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    delivery_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Financial & Growth
    annual_revenue_range: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    growth_target: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Geographic & Partner Preferences
    operating_regions: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(50)), nullable=True)
    willing_cross_border: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    preferred_partner_profile: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exclusion_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Meta
    embedding_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="profile")
