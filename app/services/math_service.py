import math
import sys
from numbers import Real


class MathService:
    def fibonacci(self, n: int) -> int:
        if n < 0:
            raise ValueError("Input for Fibonacci must be a non-negative integer.")
        if n > 90:  # Limitam pentru a preveni numere prea mari pentru un float standard
            raise ValueError("Input for Fibonacci is too large. Max supported is 90.")
        if n <= 1:
            return n

        a, b = 0, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return b

    def power(self, base: float, exponent: float) -> float|complex:
        """Calculates base to the power of exponent."""

        if exponent == 0:
            if base == 0:
                raise ValueError("0 to the power of 0 is undefined.")
            return 1

        if base == 0:
            if isinstance(exponent, Real) and exponent < 0:
                raise ValueError("0 cannot be raised to a negative power.")
            if isinstance(exponent, complex) and exponent.real < 0:
                raise ValueError("0 cannot be raised to a negative complex power.")
            return 0

        try:
            if isinstance(base, Real) and isinstance(exponent, Real):
                # math.pow e mai rapid in C, dar nu suporta baza negativa si exponenti fractionari
                if base >= 0 or exponent.is_integer():
                    result = math.pow(base, exponent)
                else:
                    # ex. (-1) ** 0.5 → complex
                    result = pow(base, exponent)
            else:
                # Pentru baze sau exponenti care nu sunt reali, folosim pow
                result = pow(base, exponent)

        except ZeroDivisionError as e:
            raise ValueError(f"Division by zero in power calculation: {e}") from e
        except OverflowError as e:
            raise OverflowError(f"exceeds maximum float {e}") from e
        except ValueError as e:
            raise ValueError(f"Invalid inputs for exponentiation: {e}") from e
        except Exception as e:
            raise ValueError(f"An unexpected error occurred during power calculation: {e}") from e

        if isinstance(result, complex):
            if abs(result.imag) < 1e-10:
                real = result.real
                if abs(real) > sys.float_info.max:
                    raise OverflowError(
                        f"Result {real} exceeds maximum float {sys.float_info.max}"
                    )
                return real
            # genuinely complex magnitude check
            if abs(result) > sys.float_info.max:
                raise OverflowError(
                    f"Result magnitude {abs(result)} exceeds maximum float {sys.float_info.max}"
                )
        else:
            # result is a real float
            if abs(result) > sys.float_info.max:
                raise OverflowError(
                    f"Result {result} exceeds maximum float {sys.float_info.max}"
                )

        return result

    def factorial(self, n: int) -> int:
        """Calculates the factorial of a number."""
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers.")
        # Limitam input-ul pentru a preveni calcule foarte lungi
        if n > 20:
            raise ValueError("Input for Factorial is too large. Max supported is 20.")
        return math.factorial(n)

# Cream o instanta singleton a serviciului pe care o vom folosi in toata aplicatia
math_service = MathService()