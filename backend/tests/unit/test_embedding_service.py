import pytest
from unittest.mock import patch, MagicMock


def test_get_embedding_empty_text():
    from app.services.embedding_service import get_embedding
    result = get_embedding("")
    assert result == []


def test_embedding_model_version_tag():
    from app.core.config import settings
    assert settings.EMBEDDING_MODEL_VERSION is not None
    assert len(settings.EMBEDDING_MODEL_VERSION) > 0


def test_build_embedding_text():
    from app.services.embedding_service import build_embedding_text
    profile = MagicMock()
    profile.business_scope = "test scope"
    profile.products_services = ["item1", "item2"]
    profile.industry_sector = "IT"
    profile.quality_standards = ["ISO 9001"]
    profile.preferred_partner_profile = "tech company"
    profile.growth_target = "expand to EU"
    text = build_embedding_text(profile)
    assert "test scope" in text
    assert "item1" in text
    assert "ISO 9001" in text
