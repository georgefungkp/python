import math
# Prime Factorization and Factor Finding Functions
# This file contains functions to find factors of numbers and prime factorizations

def get_factors(n):
    """
    Find all factors of a number using trial division.

    Time Complexity: O(sqrt(n))
    Space Complexity: O(number of factors)

    Parameters:
        n (int): The number to find factors for

    Returns:
        list: Sorted list of all factors of n
    """
    factors = []
    # Only need to check up to the square root of n
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:  # If i is a factor
            factors.append(i)  # Add i as a factor
            # If n/i is different from i, add it as well
            if i != n // i:  
                factors.append(n // i)

    # Return the sorted list of factors
    return sorted(factors)


def prime_factorization(n):
    """
    Find the prime factorization of a number.

    Time Complexity: O(sqrt(n))
    Space Complexity: O(log n)

    Parameters:
        n (int): The number to factorize

    Returns:
        dict: Dictionary with prime factors as keys and their exponents as values
    """
    factors = {}

    # Handle special cases
    if n <= 1:
        return factors

    # Check for factor 2 separately to optimize loop
    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2

    # Check odd factors up to sqrt(n)
    for i in range(3, int(n**0.5) + 1, 2):
        while n % i == 0:
            factors[i] = factors.get(i, 0) + 1
            n //= i

    # If n is a prime number greater than 2
    if n > 2:
        factors[n] = factors.get(n, 0) + 1

    return factors


def is_prime(n):
    """
    Check if a number is prime using trial division.

    Time Complexity: O(sqrt(n))
    Space Complexity: O(1)

    Parameters:
        n (int): The number to check

    Returns:
        bool: True if n is prime, False otherwise
    """
    # Handle special cases
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    # Check all potential factors of form 6k±1 up to sqrt(n)
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6

    return True


# Test the functions
if __name__ == "__main__":
    test_numbers = [12, 17, 36, 100, 1001]

    for num in test_numbers:
        print(f"\nNumber: {num}")
        print(f"Factors: {get_factors(num)}")
        print(f"Prime factorization: {prime_factorization(num)}")
        print(f"Is prime: {is_prime(num)}")
def find_factors(n):
    factors = set()
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(factors)

print(find_factors(12))  # Output: [1, 2, 3, 4, 6, 12]