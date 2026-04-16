import pytest
from httpx import AsyncClient


async def test_get_matches_unauthenticated_401(client: AsyncClient):
    response = await client.get("/api/v1/matches")
    assert response.status_code == 403


async def test_get_matches_no_profile_400(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={"email": "match1@example.com", "password": "password123"})
    token = reg.json()["access_token"]
    response = await client.get("/api/v1/matches", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
