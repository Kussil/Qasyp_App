import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str = "user@example.com"):
    reg = await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    return reg.json()["access_token"]


async def test_get_me_200(client: AsyncClient):
    token = await _register_and_login(client)
    response = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


async def test_set_role_buyer(client: AsyncClient):
    token = await _register_and_login(client, "buyer@example.com")
    response = await client.patch(
        "/api/v1/users/me/role",
        json={"role": "buyer"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "buyer"


async def test_set_role_supplier(client: AsyncClient):
    token = await _register_and_login(client, "supplier@example.com")
    response = await client.patch(
        "/api/v1/users/me/role",
        json={"role": "supplier"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "supplier"


async def test_set_role_unauthenticated_401(client: AsyncClient):
    response = await client.patch("/api/v1/users/me/role", json={"role": "buyer"})
    assert response.status_code == 403
