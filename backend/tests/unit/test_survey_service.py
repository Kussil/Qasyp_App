import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from app.services.survey_service import (
    load_survey_config, get_questions_for_role, validate_bin, validate_profile_data
)


def test_load_config_valid():
    config = load_survey_config()
    assert "sections" in config
    assert len(config["sections"]) == 4


def test_filter_questions_buyer():
    sections = get_questions_for_role("buyer")
    assert len(sections) > 0
    for section in sections:
        for q in section["questions"]:
            assert "buyer" in q.get("roles", ["buyer"])


def test_filter_questions_supplier():
    sections = get_questions_for_role("supplier")
    assert len(sections) > 0


def test_conditional_vat_shown():
    config = load_survey_config()
    legal_section = next(s for s in config["sections"] if s["id"] == "legal")
    vat_cert_q = next(q for q in legal_section["questions"] if q["id"] == "vat_certificate_number")
    assert vat_cert_q.get("conditional_on") == {"field": "vat_registered", "value": True}


def test_conditional_vat_hidden():
    # VAT cert is optional (conditional_on vat_registered=true), required=False when not VAT registered
    config = load_survey_config()
    legal_section = next(s for s in config["sections"] if s["id"] == "legal")
    vat_cert_q = next(q for q in legal_section["questions"] if q["id"] == "vat_certificate_number")
    assert vat_cert_q.get("required") is False


def test_validate_bin_valid():
    assert validate_bin("123456789012") is True


def test_validate_bin_invalid():
    assert validate_bin("12345") is False
    assert validate_bin("12345678901a") is False


def test_validate_profile_data_missing_field():
    with pytest.raises(HTTPException) as exc:
        validate_profile_data({}, "buyer")
    assert exc.value.status_code == 422


def test_validate_bin_in_profile_data():
    data = {
        "company_name": "Test", "bin": "INVALID", "legal_entity_type": "TOO",
        "vat_registered": False, "industry_sector": "IT", "business_scope": "Test",
        "products_services": ["test"], "operating_regions": ["ALMATY_CITY"]
    }
    with pytest.raises(HTTPException) as exc:
        validate_profile_data(data, "buyer")
    assert exc.value.status_code == 422
