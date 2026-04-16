import pytest
from httpx import AsyncClient
from unittest.mock import patch


async def _register_and_get_token(client: AsyncClient, email: str = "demo@example.com") -> str:
    reg = await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    return reg.json()["access_token"]


async def test_demo_upgrade_unauthenticated_403(client: AsyncClient):
    response = await client.post("/api/v1/demo/upgrade")
    assert response.status_code == 403


async def test_demo_upgrade_demo_mode_true(client: AsyncClient):
    token = await _register_and_get_token(client, "demo1@example.com")
    with patch("app.services.tier_service.settings") as mock_settings:
        mock_settings.DEMO_MODE = True
        response = await client.post(
            "/api/v1/demo/upgrade",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert response.json()["tier"] == "basic"


async def test_demo_upgrade_demo_mode_false(client: AsyncClient):
    token = await _register_and_get_token(client, "demo2@example.com")
    with patch("app.services.tier_service.settings") as mock_settings:
        mock_settings.DEMO_MODE = False
        response = await client.post(
            "/api/v1/demo/upgrade",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 404
