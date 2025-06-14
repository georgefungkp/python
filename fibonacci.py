def fibonacci(n):
    # Initialize memoization array
    dp = [0, 1] + [0] * (n - 1)

    # Fill up the memoization array
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]

def fibonacci_memo(n, memo=None):
    if memo is None:
        memo = {}

    if n in memo:
        return memo[n]
# Fibonacci Sequence Implementation
# The Fibonacci sequence is a series of numbers where each number is the sum of the two preceding ones,
# usually starting with 0 and 1.

def fibonacci_recursive(n):
    """
    Calculate the nth Fibonacci number using recursion.

    This is a simple but inefficient implementation due to repeated calculations.
    Time Complexity: O(2^n) - exponential
    Space Complexity: O(n) for the recursion stack

    Parameters:
        n (int): The position in the Fibonacci sequence (0-indexed)

    Returns:
        int: The nth Fibonacci number
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)


def fibonacci_iterative(n):
    """
    Calculate the nth Fibonacci number using iteration.

    This is more efficient than the recursive approach as it avoids repeated calculations.
    Time Complexity: O(n) - linear
    Space Complexity: O(1) - constant

    Parameters:
        n (int): The position in the Fibonacci sequence (0-indexed)

    Returns:
        int: The nth Fibonacci number
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1

    a, b = 0, 1
    for _ in range(2, n+1):
        a, b = b, a + b
    return b


def fibonacci_dynamic(n, memo={}):
    """
    Calculate the nth Fibonacci number using dynamic programming with memoization.

    This approach caches previously calculated values to avoid redundant calculations.
    Time Complexity: O(n) - linear
    Space Complexity: O(n) for the memoization table

    Parameters:
        n (int): The position in the Fibonacci sequence (0-indexed)
        memo (dict): Dictionary to store previously calculated values

    Returns:
        int: The nth Fibonacci number
    """
    if n in memo:
        return memo[n]

    if n <= 0:
        return 0
    elif n == 1:
        return 1

    memo[n] = fibonacci_dynamic(n-1, memo) + fibonacci_dynamic(n-2, memo)
    return memo[n]


# Test cases
if __name__ == "__main__":
    # Test all three implementations
    print("Testing Fibonacci implementations:")
    for i in range(10):
        print(f"F({i}) = {fibonacci_iterative(i)}")

    # Warning about recursive approach for large numbers
    print("\nWarning: Recursive approach is very slow for large numbers")

    # Example of large Fibonacci number using efficient methods
    n = 35
    print(f"F({n}) = {fibonacci_dynamic(n)}")
    if n <= 1:
        return n

    # Recursively solve subproblems and cache the results
    memo[n] = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)

    return memo[n]



print(fibonacci(10))