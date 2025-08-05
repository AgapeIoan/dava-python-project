import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.db.models import ApiRequest

@pytest.mark.asyncio
async def test_calculate_power_happy_path(client: AsyncClient, api_key_headers: dict, db_session):
    """
    Tests the happy path for calculating power.

    This test verifies that the API correctly calculates the power of a base raised to an exponent
    and logs the operation in the audit database.

    Args:
        client (AsyncClient): The HTTP client for testing.
        api_key_headers (dict): The authentication headers containing the API key.
        db_session (AsyncSession): The database session instance.

    Asserts:
        - The response status code is 200.
        - The result matches the expected value.
        - The operation is logged in the audit database.
    """
    response = await client.post(
        "/api/v1/power",
        json={"base": "2", "exponent": "8"},
        headers=api_key_headers,
    )
    response = await client.get("/api/v1/power", params={"base": 2, "exponent": 8}, headers=api_key_headers)
    assert response.status_code == 200
    assert str(response.json()["result"]) == "256.0"

    result = await db_session.execute(select(ApiRequest))
    log_entry = result.scalar_one_or_none()
    assert log_entry is not None
    assert log_entry.operation_type == "power"

@pytest.mark.asyncio
async def test_api_power_strips_tiny_imaginary_part(client: AsyncClient, api_key_headers: dict):
    """
    Tests that the API strips tiny imaginary parts from complex numbers.

    Args:
        client (AsyncClient): The HTTP client for testing.
        api_key_headers (dict): The authentication headers containing the API key.

    Asserts:
        - The response status code is 200.
        - The result matches the expected value without imaginary parts.
    """
    payload = {"base": "2+0j", "exponent": "2"}
    response = await client.post(
        "/api/v1/power", json=payload, headers=api_key_headers
    )
    response = await client.get("/api/v1/power", params={"base": "2", "exponent": "2"}, headers=api_key_headers)
    assert response.status_code == 200
    assert str(response.json()["result"]) == "4.0"

@pytest.mark.asyncio
async def test_api_power_with_complex_numbers(client: AsyncClient, api_key_headers: dict):
    """
    Tests the API's ability to handle complex numbers.

    Args:
        client (AsyncClient): The HTTP client for testing.
        api_key_headers (dict): The authentication headers containing the API key.

    Asserts:
        - The response status code is 200.
        - The result contains complex numbers.
    """
    payload = {"base": "-2+5j", "exponent": "2+1j"}
    response = await client.post(
        "/api/v1/power", json=payload, headers=api_key_headers
    )
    response = await client.get("/api/v1/power", params={"base": "-2+5j", "exponent": "2+1j"}, headers=api_key_headers)
    assert response.status_code == 200
    assert "j" in response.json()["result"]

@pytest.mark.asyncio
async def test_api_power_missing_api_key(client: AsyncClient):
    """
    Tests the API's response when the API key is missing.

    Args:
        client (AsyncClient): The HTTP client for testing.

    Asserts:
        - The response status code is 400.
        - The error detail indicates the API key is missing.
    """
    response = await client.post("/api/v1/power", json={"base": "2", "exponent": "3"})
    response = await client.get("/api/v1/power", params={"base": 2, "exponent": 3})
    assert response.status_code == 400
    assert response.json()["detail"] == "API Key is missing"

@pytest.mark.asyncio
async def test_api_power_invalid_key(client: AsyncClient):
    """
    Tests the API's response when an invalid API key is provided.

    Args:
        client (AsyncClient): The HTTP client for testing.

    Asserts:
        - The response status code is 400.
        - The error detail indicates the API key format is invalid.
    """
    headers = {"X-API-Key": "invalid_key_format"}
    response = await client.get("/api/v1/power", params={"base": "2", "exponent": "3"}, headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid API Key format"
