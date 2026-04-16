import pytest
from unittest.mock import MagicMock
from app.services.matching_service import build_qdrant_filter, COMPLEMENTARY_ROLE


def test_buyer_never_matches_buyer():
    profile = MagicMock()
    profile.role = "BUYER"
    profile.willing_cross_border = True
    f = build_qdrant_filter(profile)
    role_filter = next(c for c in f["must"] if c["key"] == "role")
    assert role_filter["match"]["value"] != "BUYER"


def test_supplier_never_matches_supplier():
    profile = MagicMock()
    profile.role = "SUPPLIER"
    profile.willing_cross_border = True
    f = build_qdrant_filter(profile)
    role_filter = next(c for c in f["must"] if c["key"] == "role")
    assert role_filter["match"]["value"] != "SUPPLIER"


def test_cross_border_includes_all_regions():
    profile = MagicMock()
    profile.role = "BUYER"
    profile.willing_cross_border = True
    profile.operating_regions = ["ALMATY_CITY"]
    f = build_qdrant_filter(profile)
    # No region filter when cross-border
    assert "should" not in f or f.get("should") is None


def test_no_overlap_no_results():
    profile = MagicMock()
    profile.role = "BUYER"
    profile.willing_cross_border = False
    profile.operating_regions = []
    f = build_qdrant_filter(profile)
    # No operating regions = should not have region should conditions
    assert "should" not in f
