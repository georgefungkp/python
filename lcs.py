# Longest Common Subsequence (LCS) implementation using Dynamic Programming
# The LCS finds the longest subsequence common to two sequences

def lcs_length(X, Y):
    """
    Computes the length of the Longest Common Subsequence (LCS) between two sequences.

    A subsequence is a sequence that can be derived from another sequence by deleting
    some or no elements without changing the order of the remaining elements.

    Args:
        X (str or List): First sequence
        Y (str or List): Second sequence

    Returns:
        int: Length of the longest common subsequence

    Example:
        >>> lcs_length("ABCBDAB", "BDCABA")
        4  # The LCS is "BCBA" with length 4
    """
    m = len(X)
    n = len(Y)

    # Initialize DP table with zeros
    # dp[i][j] represents the length of LCS of X[0..i-1] and Y[0..j-1]
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    # Fill the DP table bottom-up
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                # If current characters match, extend the LCS
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                # Take the maximum from excluding either current character
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return dp[m][n]


def lcs_string(X, Y):
    """
    Computes the Longest Common Subsequence (LCS) between two sequences and returns it.

    Args:
        X (str or List): First sequence
        Y (str or List): Second sequence

    Returns:
        str or List: The longest common subsequence

    Example:
        >>> lcs_string("ABCBDAB", "BDCABA")
        "BCBA"  # The LCS is "BCBA"
    """
    m = len(X)
    n = len(Y)

    # Initialize DP table
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Backtrack to find the LCS
    i, j = m, n
    lcs = []

    while i > 0 and j > 0:
        if X[i-1] == Y[j-1]:
            lcs.append(X[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1

    # Reverse the LCS and convert to the same type as input
    lcs.reverse()

    # If input was a string, return as string, otherwise as a list
    if isinstance(X, str) and isinstance(Y, str):
        return ''.join(lcs)
    return lcs


# Example usage
if __name__ == "__main__":
    # Example 1: String sequences
    X = "ABCBDAB"
    Y = "BDCABA"

    length = lcs_length(X, Y)
    print(f"Length of LCS: {length}")

    subsequence = lcs_string(X, Y)
    print(f"LCS: {subsequence}")

    # Example 2: List sequences
    X_list = [1, 3, 5, 7, 9, 11]
    Y_list = [1, 2, 3, 5, 8, 9, 10]

    length = lcs_length(X_list, Y_list)
    print(f"\nLength of LCS: {length}")

    subsequence = lcs_string(X_list, Y_list)
    print(f"LCS: {subsequence}")
