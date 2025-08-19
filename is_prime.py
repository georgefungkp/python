import math


def isPrime(n):

    # Numbers less than or equal to 1 are not prime
    if n <= 1:
        return False

    # Check divisibility from 2 to the square root of n
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False

    # If no divisors were found, n is prime
    return True


def isPrime(n):
    # ## The Mathematical Pattern
    # All prime numbers greater than 3 can be expressed in the form **6k±1** (where k is a positive integer). This means they're either:
    # - 6k - 1 (like 5, 11, 17, 23, 29...)
    # - 6k + 1 (like 7, 13, 19, 31, 37...)
    #
    # ## Why This Works
    # Numbers that are NOT of the form 6k±1 are always composite:
    # - **6k** is divisible by 6
    # - **6k+2** is divisible by 2
    # - **6k+3** is divisible by 3
    # - **6k+4** is divisible by 2

    if n <= 1:
        return False

    # Check if n is 2 or 3
    if n == 2 or n == 3:
        return True

    # Check whether n is divisible by 2 or 3
    if n % 2 == 0 or n % 3 == 0:
        return False

    # Check from 5 to square root of n
    # Iterate i by (i+6)
    i = 5
    while i <= math.sqrt(n):
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6

    return True