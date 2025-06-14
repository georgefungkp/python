#!/usr/bin/env python3

"""
Longest Common Subsequence (LCS) Algorithm Implementation

This module implements the Longest Common Subsequence algorithm using dynamic programming.
LCS finds the longest subsequence that is present in two sequences in the same relative order.

The module provides the following functions:
- lcs_length: Computes the length of the LCS between two sequences
- lcs_string: Computes and returns the actual LCS between two sequences
- lcs_with_traceback: Computes the LCS and provides a traceback for visualization
- print_lcs_traceback: Prints a visual representation of the LCS traceback

Time Complexity: O(m*n) where m and n are the lengths of the two sequences
Space Complexity: O(m*n) for the dynamic programming table

References:
- Introduction to Algorithms by Cormen, Leiserson, Rivest, and Stein
- https://en.wikipedia.org/wiki/Longest_common_subsequence_problem

Author: AI Assistant
Date: 2025-06-14
"""

from typing import List, TypeVar, Sequence, Union, Optional, Tuple

T = TypeVar('T')  # Generic type for sequence elements


def lcs_length(X: Sequence[T], Y: Sequence[T]) -> int:
    """
    Computes the length of the Longest Common Subsequence (LCS) between two sequences.

    A subsequence is a sequence that can be derived from another sequence by deleting
    some or no elements without changing the order of the remaining elements.

    Args:
        X: First sequence (string or list)
        Y: Second sequence (string or list)

    Returns:
        The length of the longest common subsequence

    Example:
        >>> lcs_length("ABCBDAB", "BDCABA")
        4  # The LCS is "BCBA" with length 4
    """
    # Get sequence lengths
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


def lcs_string(X: Sequence[T], Y: Sequence[T]) -> Union[str, List[T]]:
    """
    Computes and returns the actual Longest Common Subsequence between two sequences.

    This function first builds a dynamic programming table to find the LCS length,
    then backtracks through the table to reconstruct the actual subsequence.

    Args:
        X: First sequence (string or list)
        Y: Second sequence (string or list)

    Returns:
        The longest common subsequence as a string (if inputs are strings)
        or as a list (if inputs are lists)

    Example:
        >>> lcs_string("ABCBDAB", "BDCABA")
        'BCBA'  # The LCS is "BCBA"
    """
    # Get sequence lengths
    m = len(X)
    n = len(Y)

    # Initialize DP table with zeros
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    # Fill the DP table using the same logic as lcs_length
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Backtrack to find the actual LCS
    lcs: List[T] = []
    i, j = m, n

    # Start from the bottom-right cell and move towards the top-left
    while i > 0 and j > 0:
        if X[i-1] == Y[j-1]:
            # If characters match, this character is part of the LCS
            lcs.append(X[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            # If the value from the cell above is greater, move up
            i -= 1
        else:
            # Otherwise, move left
            j -= 1

    # Reverse the LCS since we built it backwards
    lcs.reverse()

    # Return the appropriate type based on input types
    if isinstance(X, str) and isinstance(Y, str):
        return ''.join(lcs)
    return lcs


def lcs_with_traceback(X: Sequence[T], Y: Sequence[T]) -> Tuple[int, Union[str, List[T]], List[List[int]], List[List[str]]]:
    """
    Computes the LCS and provides a traceback for visualization.

    Args:
        X: First sequence
        Y: Second sequence

    Returns:
        A tuple containing:
        - Length of the LCS
        - The LCS itself
        - The DP table used for calculation
        - A traceback table showing the path used to construct the LCS
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

    # Create traceback
    traceback = [[' ' for _ in range(n + 1)] for _ in range(m + 1)]

    # Backtrack to find the LCS and mark the path
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if X[i-1] == Y[j-1]:
            lcs.append(X[i-1])
            traceback[i][j] = '↖'  # diagonal
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            traceback[i][j] = '↑'  # up
            i -= 1
        else:
            traceback[i][j] = '←'  # left
            j -= 1

    lcs.reverse()

    # Convert to string if input was string
    if isinstance(X, str) and isinstance(Y, str):
        lcs_result = ''.join(lcs)
    else:
        lcs_result = lcs

    return dp[m][n], lcs_result, dp, traceback


def print_lcs_traceback(X: Sequence[T], Y: Sequence[T], dp: List[List[int]], traceback: List[List[str]]) -> None:
    """
    Prints a visual representation of the LCS traceback.

    Args:
        X: First sequence
        Y: Second sequence
        dp: The dynamic programming table
        traceback: The traceback markers
    """
    print("\nLCS Traceback Visualization:")

    # Print the header with Y sequence
    print("    ", end="")
    for j in range(len(Y)):
        print(f" {Y[j]} ", end="")
    print()

    # Print each row
    for i in range(len(X) + 1):
        if i == 0:
            print("  ", end="")
        else:
            print(f"{X[i-1]} ", end="")

        for j in range(len(Y) + 1):
            print(f"{dp[i][j]}{traceback[i][j]}", end=" ")
        print()


def lcs_memoization(X: Sequence[T], Y: Sequence[T]) -> int:
    """
    Computes the length of the Longest Common Subsequence using memoization (top-down approach).

    This implementation uses recursion with memoization instead of the tabulation (bottom-up) approach.

    Args:
        X: First sequence (string or list)
        Y: Second sequence (string or list)

    Returns:
        The length of the longest common subsequence
    """
    # Create memo table initialized with -1 (indicating not computed yet)
    memo = [[-1 for _ in range(len(Y) + 1)] for _ in range(len(X) + 1)]

    # Recursive helper function with memoization
    def lcs_memo_helper(i: int, j: int) -> int:
        # Base case: if either sequence is empty, LCS is 0
        if i == 0 or j == 0:
            return 0

        # If already computed, return memoized result
        if memo[i][j] != -1:
            return memo[i][j]

        # If current characters match, add 1 to LCS of remaining sequences
        if X[i-1] == Y[j-1]:
            memo[i][j] = 1 + lcs_memo_helper(i-1, j-1)
        else:
            # Take maximum of LCS by excluding either current character
            memo[i][j] = max(lcs_memo_helper(i-1, j), lcs_memo_helper(i, j-1))

        return memo[i][j]

    # Start recursive computation from the end of both sequences
    return lcs_memo_helper(len(X), len(Y))


# Example usage
if __name__ == "__main__":
    print("===== Longest Common Subsequence (LCS) Examples =====")

    # Example 1: String sequences
    X = "ABCBDAB"
    Y = "BDCABA"

    print(f"\nExample 1: String Sequences\nX = {X}\nY = {Y}")

    length = lcs_length(X, Y)
    print(f"Length of LCS: {length}")

    subsequence = lcs_string(X, Y)
    print(f"LCS: {subsequence}")

    # With traceback visualization
    _, _, dp, traceback = lcs_with_traceback(X, Y)
    print_lcs_traceback(X, Y, dp, traceback)

    # Example 2: List sequences
    X_list = [1, 3, 5, 7, 9, 11]
    Y_list = [1, 2, 3, 5, 8, 9, 10]

    print(f"\nExample 2: List Sequences\nX = {X_list}\nY = {Y_list}")

    length = lcs_length(X_list, Y_list)
    print(f"Length of LCS: {length}")

    subsequence = lcs_string(X_list, Y_list)
    print(f"LCS: {subsequence}")

    # Example 3: Empty sequence case
    X_empty = ""
    Y_example = "ABCD"

    print(f"\nExample 3: Empty Sequence\nX = '{X_empty}'\nY = '{Y_example}'")
    print(f"Length of LCS: {lcs_length(X_empty, Y_example)}")
    print(f"LCS: '{lcs_string(X_empty, Y_example)}'")

    # Example 4: Using memoization approach
    print(f"\nExample 4: Using Memoization\nX = {X}\nY = {Y}")
    length_memo = lcs_memoization(X, Y)
    print(f"Length of LCS (using memoization): {length_memo}")