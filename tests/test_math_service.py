import pytest
from app.services.math_service import math_service

def test_factorial_happy_path():
    """Testeaza cazurile normale pentru factorial."""
    assert math_service.factorial(5) == 120
    assert math_service.factorial(0) == 1
    assert math_service.factorial(1) == 1


def test_factorial_error_cases():
    """Testeaza cazurile care ar trebui sa arunce o eroare."""
    # Verificam ca o eroare de tip ValueError este aruncata pentru input negativ
    with pytest.raises(ValueError):
        math_service.factorial(-1)

    # Verificam mesajul specific al erorii pentru input prea mare
    with pytest.raises(ValueError, match="Input for Factorial is too large"):
        math_service.factorial(21)

def test_power_happy_path():
    """Testeaza cazurile normale pentru power."""
    assert math_service.power(2, 10) == 1024
    assert math_service.power(9, 0.5) == 3
    assert math_service.power(5, -1) == 0.2
    assert math_service.power(10, 0) == 1


def test_power_error_cases():
    """Testeaza cazul de eroare 0 la putere negativa."""
    with pytest.raises(ValueError, match="0 cannot be raised to a negative power"):
        math_service.power(0, -1)

def test_fibonacci_happy_path():
    """Testeaza cazurile normale pentru fibonacci."""
    assert math_service.fibonacci(0) == 0
    assert math_service.fibonacci(1) == 1
    assert math_service.fibonacci(2) == 1
    assert math_service.fibonacci(10) == 55
    assert math_service.fibonacci(20) == 6765


def test_fibonacci_error_cases():
    """Testeaza cazurile de eroare pentru fibonacci."""
    # Testeaza cazul de eroare pentru input negativ
    with pytest.raises(ValueError, match="Input for Fibonacci must be a non-negative integer"):
        math_service.fibonacci(-1)

    # Testeaza cazul de eroare pentru input prea mare
    with pytest.raises(ValueError, match="Input for Fibonacci is too large"):
        math_service.fibonacci(91)