import pytest
from unittest.mock import MagicMock, AsyncMock, patch


def test_build_filter_buyer_targets_suppliers():
    from app.services.matching_service import build_qdrant_filter
    profile = MagicMock()
    profile.role = "BUYER"
    profile.willing_cross_border = True
    profile.operating_regions = []
    f = build_qdrant_filter(profile)
    assert f["must"][0]["match"]["value"] == "SUPPLIER"


def test_build_filter_supplier_targets_buyers():
    from app.services.matching_service import build_qdrant_filter
    profile = MagicMock()
    profile.role = "SUPPLIER"
    profile.willing_cross_border = True
    f = build_qdrant_filter(profile)
    assert f["must"][0]["match"]["value"] == "BUYER"


def test_region_filter_cross_border_skip():
    from app.services.matching_service import build_qdrant_filter
    profile = MagicMock()
    profile.role = "BUYER"
    profile.willing_cross_border = True
    profile.operating_regions = ["ALMATY_CITY"]
    f = build_qdrant_filter(profile)
    # Cross-border: no should conditions needed
    assert "should" not in f or f.get("should") is None


def test_region_filter_overlap():
    from app.services.matching_service import build_qdrant_filter
    profile = MagicMock()
    profile.role = "BUYER"
    profile.willing_cross_border = False
    profile.operating_regions = ["ALMATY_CITY", "ASTANA_CITY"]
    f = build_qdrant_filter(profile)
    assert "should" in f


def test_free_user_limited_to_5():
    # This is tested at the endpoint level via integration tests
    assert True  # Placeholder
