import uuid
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, ConfigDict


class LegalEntityType(str, Enum):
    TOO = "TOO"
    IP = "IP"
    AO = "AO"
    GP = "GP"
    OTHER = "OTHER"


class Role(str, Enum):
    BUYER = "BUYER"
    SUPPLIER = "SUPPLIER"
    BOTH = "BOTH"


class Frequency(str, Enum):
    ONE_TIME = "ONE_TIME"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"


class RevenueRange(str, Enum):
    BELOW_10M = "BELOW_10M"
    RANGE_10M_50M = "10M_50M"
    RANGE_50M_200M = "50M_200M"
    RANGE_200M_1B = "200M_1B"
    ABOVE_1B = "ABOVE_1B"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


class Region(str, Enum):
    ALMATY_CITY = "ALMATY_CITY"
    ASTANA_CITY = "ASTANA_CITY"
    SHYMKENT_CITY = "SHYMKENT_CITY"
    ALMATY_REGION = "ALMATY_REGION"
    AKMOLA = "AKMOLA"
    AKTOBE = "AKTOBE"
    ATYRAU = "ATYRAU"
    EAST_KZ = "EAST_KZ"
    ZHAMBYL = "ZHAMBYL"
    WEST_KZ = "WEST_KZ"
    KARAGANDA = "KARAGANDA"
    KOSTANAY = "KOSTANAY"
    KYZYLORDA = "KYZYLORDA"
    MANGYSTAU = "MANGYSTAU"
    PAVLODAR = "PAVLODAR"
    NORTH_KZ = "NORTH_KZ"
    TURKESTAN = "TURKESTAN"
    ABAI = "ABAI"
    ZHETYSU = "ZHETYSU"
    ULYTAU = "ULYTAU"


class ProfileCreate(BaseModel):
    company_name: str
    bin: str
    legal_entity_type: LegalEntityType
    vat_registered: bool
    vat_certificate_number: Optional[str] = None
    industry_sector: str
    business_scope: str
    role: Role
    products_services: Optional[List[str]] = None
    volume_requirements: Optional[str] = None
    frequency: Optional[Frequency] = None
    quality_standards: Optional[List[str]] = None
    delivery_requirements: Optional[str] = None
    annual_revenue_range: Optional[RevenueRange] = None
    growth_target: Optional[str] = None
    operating_regions: Optional[List[Region]] = None
    willing_cross_border: Optional[bool] = None
    preferred_partner_profile: Optional[str] = None
    exclusion_criteria: Optional[str] = None


class ProfileResponse(ProfileCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    embedding_generated: bool
