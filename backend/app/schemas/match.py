import uuid
from typing import Optional, List
from pydantic import BaseModel


class MatchResult(BaseModel):
    profile_id: Optional[uuid.UUID]
    company_name: str
    industry_sector: Optional[str] = None
    operating_regions: Optional[List[str]] = None
    match_score: Optional[float]
    explanation: Optional[str] = None
    locked: bool = False


class MatchListResponse(BaseModel):
    matches: List[MatchResult]
    total: int
    has_more: bool
