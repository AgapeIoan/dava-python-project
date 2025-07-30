import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.db.models import ApiRequest
from app.main import app
from app.core.config import settings
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def get_auth_headers():
    # Poți înlocui acest token cu unul real dacă e necesar
    token = "test_token"
    return {"Authorization": f"Bearer {token}"}


@patch("app.core.redis_cache.cache", new_callable=AsyncMock)
@patch("app.core.redis_logger.redis_client", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_calculate_power_happy_path(mock_redis_logger, mock_redis_cache, db_setup_and_teardown):
    mock_redis_logger.xadd.return_value = None
    mock_redis_cache.get.return_value = None
    mock_redis_cache.set.return_value = None

    headers = get_auth_headers()
    response = client.post("/apikeys", json={"expires_in_seconds": 60}, headers=headers)
    assert response.status_code == 200

    session = db_setup_and_teardown
    result = await session.execute(select(ApiRequest).order_by(ApiRequest.timestamp.desc()))
    log_entry = result.scalar_one_or_none()

    assert log_entry is not None
    assert log_entry.operation_type == "power"
    mock_redis_logger.xadd.assert_called()


@patch("app.core.redis_cache.cache", new_callable=AsyncMock)
@patch("app.core.redis_logger.redis_client", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_api_power_strips_tiny_imaginary_part(mock_redis_logger, mock_redis_cache, db_setup_and_teardown):
    mock_redis_logger.xadd.return_value = None
    mock_redis_cache.get.return_value = None
    mock_redis_cache.set.return_value = None

    headers = get_auth_headers()
    response = client.post("/apikeys", json={"expires_in_seconds": 60}, headers=headers)
    assert response.status_code == 200
    api_key = response.json()["key"]

    headers[settings.API_KEY_NAME] = api_key
    response = client.post("/api/v1/power", json={"base": "2+0.000001j", "exponent": "2"}, headers=headers)

    assert response.status_code == 200
    assert str(response.json()["result"]) == "4.0"


@patch("app.core.redis_cache.cache", new_callable=AsyncMock)
@patch("app.core.redis_logger.redis_client", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_api_power_with_complex_numbers(mock_redis_logger, mock_redis_cache, db_setup_and_teardown):
    mock_redis_logger.xadd.return_value = None
    mock_redis_cache.get.return_value = None
    mock_redis_cache.set.return_value = None

    headers = get_auth_headers()
    response = client.post("/apikeys", json={"expires_in_seconds": 60}, headers=headers)
    assert response.status_code == 200
    api_key = response.json()["key"]

    headers[settings.API_KEY_NAME] = api_key
    response = client.post("/api/v1/power", json={"base": "1j", "exponent": "2"}, headers=headers)

    assert response.status_code == 200
    assert str(response.json()["result"]) == "-1.0"


@patch("app.core.redis_cache.cache", new_callable=AsyncMock)
@patch("app.core.redis_logger.redis_client", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_generate_and_use_api_key(mock_redis_logger, mock_redis_cache, db_setup_and_teardown):
    mock_redis_logger.xadd.return_value = None
    mock_redis_cache.get.return_value = None
    mock_redis_cache.set.return_value = None

    headers = get_auth_headers()
    response = client.post("/apikeys", json={"expires_in_seconds": 60}, headers=headers)
    assert response.status_code == 200
    api_key = response.json()["key"]

    headers[settings.API_KEY_NAME] = api_key
    response2 = client.post("/api/v1/power", json={"base": "3", "exponent": "2"}, headers=headers)

    assert response2.status_code == 200
    assert str(response2.json()["result"]) == "9.0"
