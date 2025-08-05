import sys
import pytest
from app.services.math_service import math_service
from unittest.mock import patch, AsyncMock

def test_factorial_happy_path():
    """
    Tests normal cases for factorial.

    Asserts:
        - Factorial of 5 is 120.
        - Factorial of 0 is 1.
        - Factorial of 1 is 1.
    """
    assert math_service.factorial(5) == 120
    assert math_service.factorial(0) == 1
    assert math_service.factorial(1) == 1


def test_factorial_error_cases():
    """
    Tests error cases for factorial.

    Asserts:
        - ValueError is raised for negative input.
        - ValueError with specific message is raised for input too large.
    """
    # Verificam ca o eroare de tip ValueError este aruncata pentru input negativ
    with pytest.raises(ValueError):
        math_service.factorial(-1)

    # Verificam mesajul specific al erorii pentru input prea mare
    with pytest.raises(ValueError, match="Input for Factorial is too large"):
        math_service.factorial(21)

def test_power_happy_path():
    """
    Tests normal cases for power.

    Asserts:
        - 2 raised to 10 is 1024.
        - 9 raised to 0.5 is 3.
        - 5 raised to -1 is 0.2.
        - 10 raised to 0 is 1.
    """
    assert math_service.power(2, 10) == 1024
    assert math_service.power(9, 0.5) == 3
    assert math_service.power(5, -1) == 0.2
    assert math_service.power(10, 0) == 1

def test_power_error_cases():
    """
    Tests error case for 0 raised to a negative power.

    Asserts:
        - ValueError with specific message is raised.
    """
    with pytest.raises(ValueError, match="0 cannot be raised to a negative power"):
        math_service.power(0, -1)

def test_power_zero_zero_error():
    """
    Tests error case for 0 raised to the power of 0.

    Asserts:
        - ValueError with message "undefined" is raised.
    """
    with pytest.raises(ValueError, match="undefined"):
        math_service.power(0, 0)

def test_negative_base_integer_exponent():
    """
    Tests negative base with integer exponent resulting in a real number.

    Asserts:
        - Result is a float.
        - Result matches the expected value.
    """
    result = math_service.power(-2, 3)
    assert isinstance(result, float)
    assert result == -8.0

def test_negative_base_fractional_exponent_complex_result():
    """
    Tests negative base with fractional exponent resulting in a complex number.

    Asserts:
        - Result is a complex number.
        - Result matches the expected value.
    """
    result = math_service.power(-1, 0.5)
    # √(−1) = 1j
    assert isinstance(result, complex)
    assert result == pytest.approx(1j)

def test_strip_tiny_imaginary_part():
    """
    Tests removal of tiny imaginary parts.

    Asserts:
        - Result is a float.
        - Result matches the expected value.
    """
    # (2+0j)**2 → 4 (float), nu 4+0j
    result = math_service.power(2+0j, 2)
    assert isinstance(result, float)
    assert result == 4

def test_zero_base_complex_negative_exponent_division_by_zero():
    """
    Tests catching ZeroDivisionError for complex negative exponent.

    Asserts:
        - ValueError with specific message is raised.
    """
    with pytest.raises(ValueError, match="Division by zero"):
        math_service.power(0, -1+0j)

def test_overflow_error_for_huge_result():
    """
    Tests OverflowError when result exceeds maximum float.

    Asserts:
        - OverflowError with specific message is raised.
    """
    # sys.float_info.max**2 → inf → OverflowError în codul nostru
    with pytest.raises(OverflowError, match="exceeds maximum float"):
        math_service.power(sys.float_info.max, 2)

def test_fibonacci_happy_path():
    """
    Tests normal cases for Fibonacci.

    Asserts:
        - Fibonacci of 0 is 0.
        - Fibonacci of 1 is 1.
        - Fibonacci of 2 is 1.
        - Fibonacci of 10 is 55.
        - Fibonacci of 20 is 6765.
    """
    assert math_service.fibonacci(0) == 0
    assert math_service.fibonacci(1) == 1
    assert math_service.fibonacci(2) == 1
    assert math_service.fibonacci(10) == 55
    assert math_service.fibonacci(20) == 6765


def test_fibonacci_error_cases():
    """
    Tests error cases for Fibonacci.

    Asserts:
        - ValueError with specific message is raised for negative input.
        - ValueError with specific message is raised for input too large.
    """
    # Testeaza cazul de eroare pentru input negativ
    with pytest.raises(ValueError, match="Input for Fibonacci must be a non-negative integer"):
        math_service.fibonacci(-1)

    # Testeaza cazul de eroare pentru input prea mare
    with pytest.raises(ValueError, match="Input for Fibonacci is too large"):
        math_service.fibonacci(91)

@pytest.mark.asyncio
@patch('app.core.decorators.redis_cache_client', new_callable=AsyncMock)
async def test_fibonacci_async_cache_hit(mock_redis_client):
    """
    Tests that the async function returns value from cache.

    Mocks:
        - Redis client to return a cached value.

    Asserts:
        - Result matches the cached value.
        - Redis client's get method is awaited once.
        - Redis client's setex method is not awaited.
    """
    # Arrange: Configuram mock-ul sa returneze o valoare cand .get() e asteptat
    mock_redis_client.get.return_value = "999"

    # Act: Apelam functia async cu await
    result = await math_service.fibonacci_async(15)

    # Assert
    assert int(result) == 999
    mock_redis_client.get.assert_awaited_once_with("fibonacci:15")
    mock_redis_client.setex.assert_not_awaited()

@pytest.mark.asyncio
@patch('app.core.decorators.redis_cache_client', new_callable=AsyncMock)
async def test_fibonacci_async_cache_miss(mock_redis_client):
    """
    Tests that the async function calculates and saves to cache.

    Mocks:
        - Redis client to simulate cache miss.

    Asserts:
        - Result matches the calculated value.
        - Redis client's get method is awaited once.
        - Redis client's setex method is awaited once with correct parameters.
    """
    # Arrange
    mock_redis_client.get.return_value = None

    # Act
    result = await math_service.fibonacci_async(10)

    # Assert
    assert result == 55
    mock_redis_client.get.assert_awaited_once_with("fibonacci:10")
    mock_redis_client.setex.assert_awaited_once_with("fibonacci:10", 3600, "55")