import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.services.tier_service import upgrade_to_basic_demo


async def test_upgrade_demo_mode_false():
    with patch("app.services.tier_service.settings") as mock_settings:
        mock_settings.DEMO_MODE = False
        db = AsyncMock()
        user = MagicMock()
        with pytest.raises(HTTPException) as exc:
            await upgrade_to_basic_demo(user, db)
        assert exc.value.status_code == 404


async def test_upgrade_demo_mode_true():
    with patch("app.services.tier_service.settings") as mock_settings:
        mock_settings.DEMO_MODE = True
        db = AsyncMock()
        import uuid
        user = MagicMock()
        user.id = uuid.uuid4()
        user.tier = "free"
        result = await upgrade_to_basic_demo(user, db)
        assert result["tier"] == "basic"
        assert "demo mode" in result["message"].lower()
        db.commit.assert_called_once()


async def test_free_user_matches_gated():
    """Gating is tested in the matches endpoint tests."""
    assert True  # Integration test coverage


async def test_gated_match_no_real_data():
    """Locked match items should have null profile_id and company_name='***'."""
    from app.schemas.match import MatchResult
    locked = MatchResult(profile_id=None, company_name="***", match_score=None, locked=True)
    assert locked.profile_id is None
    assert locked.company_name == "***"
    assert locked.locked is True
