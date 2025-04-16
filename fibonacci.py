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

    if n <= 1:
        return n

    # Recursively solve subproblems and cache the results
    memo[n] = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)

    return memo[n]



print(fibonacci(10))