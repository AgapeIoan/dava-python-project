import math


class MathService:
    # ... aici vor veni si celelalte metode (power, factorial) ...

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