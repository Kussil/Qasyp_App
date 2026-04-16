import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.services.auth_service import register_user, authenticate_user, refresh_tokens
from app.core.security import create_refresh_token


class TestRegisterUser:
    async def test_register_short_password_raises(self):
        db = AsyncMock()
        with pytest.raises(HTTPException) as exc:
            await register_user("test@example.com", "short", db)
        assert exc.value.status_code == 422

    async def test_register_duplicate_email_raises(self):
        db = AsyncMock()
        mock_user = MagicMock()
        db.execute.return_value.scalar_one_or_none.return_value = mock_user
        with pytest.raises(HTTPException) as exc:
            await register_user("test@example.com", "password123", db)
        assert exc.value.status_code == 409

    async def test_register_creates_user(self):
        db = AsyncMock()
        db.execute.return_value.scalar_one_or_none.return_value = None
        result = await register_user("new@example.com", "password123", db)
        assert "access_token" in result
        assert "refresh_token" in result
        db.add.assert_called_once()
        db.commit.assert_called_once()


class TestAuthenticateUser:
    async def test_authenticate_nonexistent_email(self):
        db = AsyncMock()
        db.execute.return_value.scalar_one_or_none.return_value = None
        with pytest.raises(HTTPException) as exc:
            await authenticate_user("no@example.com", "password", db)
        assert exc.value.status_code == 401

    async def test_authenticate_wrong_password(self):
        db = AsyncMock()
        mock_user = MagicMock()
        mock_user.hashed_password = "hashed_different"
        db.execute.return_value.scalar_one_or_none.return_value = mock_user
        with patch("app.services.auth_service.verify_password", return_value=False):
            with pytest.raises(HTTPException) as exc:
                await authenticate_user("test@example.com", "wrong", db)
        assert exc.value.status_code == 401

    async def test_authenticate_valid_credentials(self):
        db = AsyncMock()
        import uuid
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.hashed_password = "hashed"
        db.execute.return_value.scalar_one_or_none.return_value = mock_user
        with patch("app.services.auth_service.verify_password", return_value=True):
            result = await authenticate_user("test@example.com", "password123", db)
        assert "access_token" in result


class TestRefreshTokens:
    async def test_refresh_expired_token(self):
        db = AsyncMock()
        with pytest.raises(HTTPException) as exc:
            await refresh_tokens("invalid.token.here", db)
        assert exc.value.status_code == 401

    async def test_refresh_valid_token(self):
        import uuid
        user_id = str(uuid.uuid4())
        token = create_refresh_token({"sub": user_id})
        db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.is_active = True
        db.execute.return_value.scalar_one_or_none.return_value = mock_user
        result = await refresh_tokens(token, db)
        assert "access_token" in result
        assert "refresh_token" in result
