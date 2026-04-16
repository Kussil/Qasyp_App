import pytest
from httpx import AsyncClient


async def _register_set_role(client: AsyncClient, email: str = "survey@example.com", role: str = "buyer"):
    reg = await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    token = reg.json()["access_token"]
    await client.patch(
        "/api/v1/users/me/role",
        json={"role": role},
        headers={"Authorization": f"Bearer {token}"},
    )
    return token


async def test_get_questions_buyer_200(client: AsyncClient):
    token = await _register_set_role(client, "q1@example.com")
    response = await client.get(
        "/api/v1/survey/questions?role=buyer",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "sections" in response.json()


async def test_get_questions_unauthenticated_401(client: AsyncClient):
    response = await client.get("/api/v1/survey/questions")
    assert response.status_code == 403


async def test_submit_survey_missing_required_422(client: AsyncClient):
    token = await _register_set_role(client, "q2@example.com")
    response = await client.post(
        "/api/v1/survey/submit",
        json={"company_name": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


async def test_submit_survey_invalid_bin_422(client: AsyncClient):
    token = await _register_set_role(client, "q3@example.com")
    response = await client.post(
        "/api/v1/survey/submit",
        json={
            "company_name": "Test", "bin": "123", "legal_entity_type": "TOO",
            "vat_registered": False, "industry_sector": "IT", "business_scope": "Test",
            "products_services": ["test"], "operating_regions": ["ALMATY_CITY"], "role": "BUYER"
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
