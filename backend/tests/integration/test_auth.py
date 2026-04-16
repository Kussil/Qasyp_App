import pytest
from httpx import AsyncClient


@pytest.fixture
def user_data():
    return {"email": "test@example.com", "password": "password123"}


async def test_register_endpoint_201(client: AsyncClient, user_data):
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_register_duplicate_409(client: AsyncClient, user_data):
    await client.post("/api/v1/auth/register", json=user_data)
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 409


async def test_login_endpoint_200(client: AsyncClient, user_data):
    await client.post("/api/v1/auth/register", json=user_data)
    response = await client.post("/api/v1/auth/login", json=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password_401(client: AsyncClient, user_data):
    await client.post("/api/v1/auth/register", json=user_data)
    response = await client.post("/api/v1/auth/login", json={**user_data, "password": "wrong"})
    assert response.status_code == 401


async def test_refresh_endpoint_200(client: AsyncClient, user_data):
    reg = await client.post("/api/v1/auth/register", json=user_data)
    refresh_token = reg.json()["refresh_token"]
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()
