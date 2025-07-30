import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.db.models import ApiRequest

# Toate importurile de configurare au fost mutate in conftest.py

@pytest.mark.asyncio
async def test_calculate_power_happy_path(client: AsyncClient, api_key_headers: dict, db_session):
    response = await client.post(
        "/api/v1/power",
        json={"base": "2", "exponent": "8"},
        headers=api_key_headers,
    )
    assert response.status_code == 200
    assert str(response.json()["result"]) == "256.0"

    # Verificam ca s-a scris in BD-ul de audit (nu cel de log-uri stream)
    result = await db_session.execute(select(ApiRequest))
    log_entry = result.scalar_one_or_none()
    assert log_entry is not None
    assert log_entry.operation_type == "power"

@pytest.mark.asyncio
async def test_api_power_strips_tiny_imaginary_part(client: AsyncClient, api_key_headers: dict):
    payload = {"base": "2+0j", "exponent": "2"}
    response = await client.post(
        "/api/v1/power", json=payload, headers=api_key_headers
    )
    assert response.status_code == 200
    assert str(response.json()["result"]) == "4.0"

@pytest.mark.asyncio
async def test_api_power_with_complex_numbers(client: AsyncClient, api_key_headers: dict):
    payload = {"base": "-2+5j", "exponent": "2+1j"}
    response = await client.post(
        "/api/v1/power", json=payload, headers=api_key_headers
    )
    assert response.status_code == 200
    assert "j" in response.json()["result"]

@pytest.mark.asyncio
async def test_api_power_missing_api_key(client: AsyncClient):
    response = await client.post("/api/v1/power", json={"base": "2", "exponent": "3"})
    assert response.status_code == 401
    # Mesajul corect din security.py este "API Key is missing"
    assert response.json()["detail"] == "API Key is missing"

@pytest.mark.asyncio
async def test_api_power_invalid_key(client: AsyncClient):
    headers = {"X-API-Key": "invalid_key_format"}
    response = await client.post("/api/v1/power", json={"base": "2", "exponent": "3"}, headers=headers)
    assert response.status_code == 403 # Forbidden, deoarece formatul e gresit
    assert response.json()["detail"] == "Invalid API Key format"