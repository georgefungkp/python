# Longest Common Subsequence (LCS) implementation using Dynamic Programming
# The LCS finds the longest subsequence common to two sequences
# Longest Common Subsequence (LCS) Implementation

def lcs_length(X, Y):
    """
    Computes the length of the Longest Common Subsequence (LCS) between two sequences.

    The LCS is the longest sequence that can be derived from two original sequences
    by deleting some elements without changing the order of the remaining elements.

    Args:
        X (str or list): First sequence
        Y (str or list): Second sequence

    Returns:
        int: Length of the longest common subsequence

    Time Complexity: O(m*n) where m and n are the lengths of X and Y respectively
    Space Complexity: O(m*n)
    """
    m = len(X)
    n = len(Y)

    # Create a table to store the LCS lengths
    L = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill the table in bottom-up fashion
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                # If the current characters match, add 1 to the LCS length
                L[i][j] = L[i-1][j-1] + 1
            else:
                # Otherwise, take the maximum of the LCS without one of the characters
                L[i][j] = max(L[i-1][j], L[i][j-1])

    # The bottom-right cell contains the length of the LCS
    return L[m][n]


def lcs(X, Y):
    """
    Computes both the length and the actual Longest Common Subsequence (LCS)
    between two sequences.

    Args:
        X (str or list): First sequence
        Y (str or list): Second sequence

    Returns:
        tuple: (length, subsequence) where:
               - length (int) is the length of the LCS
               - subsequence (same type as X and Y) is the actual LCS

    Time Complexity: O(m*n) where m and n are the lengths of X and Y respectively
    Space Complexity: O(m*n)
    """
    m = len(X)
    n = len(Y)

    # Create a table to store the LCS lengths
    L = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill the table in bottom-up fashion
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])

    # Reconstruct the LCS from the table
    lcs_result = []
    i, j = m, n

    while i > 0 and j > 0:
        if X[i-1] == Y[j-1]:
            # If characters match, add to the LCS and move diagonally
            lcs_result.append(X[i-1])
            i -= 1
            j -= 1
        elif L[i-1][j] >= L[i][j-1]:
            # Move to the direction of the larger value
            i -= 1
        else:
            j -= 1

    # Reverse the result since we built it backwards
    lcs_result.reverse()

    # Convert the result to the same type as the input
    if isinstance(X, str) and isinstance(Y, str):
        lcs_result = ''.join(lcs_result)

    return L[m][n], lcs_result


def lcs_dp_optimized(X, Y):
    """
    Space-optimized version of the LCS algorithm that only returns the length.

    This version uses only O(min(m,n)) space instead of O(m*n).

    Args:
        X (str or list): First sequence
        Y (str or list): Second sequence

    Returns:
        int: Length of the longest common subsequence

    Time Complexity: O(m*n) where m and n are the lengths of X and Y respectively
    Space Complexity: O(min(m,n))
    """
    # Ensure X is the shorter sequence for better space efficiency
    if len(X) > len(Y):
        X, Y = Y, X

    m, n = len(X), len(Y)

    # We only need two rows of the DP table at any time
    current = [0] * (m + 1)

    for j in range(1, n + 1):
        prev = current.copy()
        for i in range(1, m + 1):
            if X[i-1] == Y[j-1]:
                current[i] = prev[i-1] + 1
            else:
                current[i] = max(current[i-1], prev[i])

    return current[m]


def print_lcs_table(X, Y, L):
    """
    Helper function to print the LCS table for educational purposes.

    Args:
        X (str or list): First sequence
        Y (str or list): Second sequence
        L (list of list): The filled LCS table
    """
    m, n = len(X), len(Y)

    # Print the header
    print("   ", end="")
    print("   ", end="")
    for j in range(n):
        print(f" {Y[j]} ", end="")
    print()

    # Print the table with row headers
    for i in range(m + 1):
        if i == 0:
            print("   ", end="")
        else:
            print(f" {X[i-1]} ", end="")

        for j in range(n + 1):
            print(f" {L[i][j]} ", end="")
        print()


def main():
    # String examples
    X = "ABCBDAB"
    Y = "BDCABA"
    print(f"Sequence X: {X}")
    print(f"Sequence Y: {Y}")

    # Calculate and print the length of LCS
    length = lcs_length(X, Y)
    print(f"\nLength of LCS: {length}")

    # Calculate and print both the length and the actual LCS
    length, subsequence = lcs(X, Y)
    print(f"\nLCS: {subsequence} (length: {length})")

    # Use the space-optimized version
    opt_length = lcs_dp_optimized(X, Y)
    print(f"\nLength of LCS (optimized): {opt_length}")

    # Demonstrate with a list example
    X_list = [1, 3, 5, 7, 9, 11]
    Y_list = [1, 2, 3, 5, 8, 9, 10, 11]
    length_list, subsequence_list = lcs(X_list, Y_list)
    print(f"\nList X: {X_list}")
    print(f"List Y: {Y_list}")
    print(f"LCS: {subsequence_list} (length: {length_list})")

    # Educational: visualize the DP table for a small example
    small_X = "ACGT"
    small_Y = "AGCT"
    print(f"\nVisualization of the LCS table for X='{small_X}' and Y='{small_Y}':\n")
    m, n = len(small_X), len(small_Y)
    L = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if small_X[i-1] == small_Y[j-1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])

    print_lcs_table(small_X, small_Y, L)
    print(f"\nThe LCS is: {lcs(small_X, small_Y)[1]}")


if __name__ == "__main__":
    main()
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
# Longest Common Subsequence (LCS) Implementation

def lcs_length(X, Y):
    """
    Find the length of the Longest Common Subsequence of two sequences.

    This function uses dynamic programming to find the length of the LCS
    between two sequences X and Y with a time complexity of O(m*n),
    where m and n are the lengths of X and Y respectively.

    Args:
        X (str or list): First sequence
        Y (str or list): Second sequence

    Returns:
        int: Length of the longest common subsequence

    Example:
        >>> lcs_length("ABCBDAB", "BDCABA")
        4  # The LCS is "BCBA" with length 4
    """
    m = len(X)
    n = len(Y)

    # Create a table to store the LCS lengths
    # dp[i][j] represents the length of LCS of X[0:i] and Y[0:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill the dp table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return dp[m][n]

def lcs(X, Y):
    """
    Find the Longest Common Subsequence of two sequences.

    This function not only calculates the length but also returns
    the actual subsequence using dynamic programming.

    Args:
        X (str or list): First sequence
        Y (str or list): Second sequence

    Returns:
        tuple: (length, subsequence) where length is an integer and
               subsequence is a string or list depending on the input type

    Example:
        >>> lcs("ABCBDAB", "BDCABA")
        (4, "BCBA")  # The LCS is "BCBA" with length 4
    """
    m = len(X)
    n = len(Y)

    # Create a table to store the LCS lengths
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill the dp table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Reconstruct the LCS
    lcs_result = []
    i, j = m, n

    while i > 0 and j > 0:
        if X[i-1] == Y[j-1]:
            lcs_result.append(X[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1

    # The result is constructed in reverse order, so reverse it
    lcs_result.reverse()

    # Convert the result to the same type as the input
    if isinstance(X, str) and isinstance(Y, str):
        lcs_result = ''.join(lcs_result)

    return dp[m][n], lcs_result

def lcs_all_sequences(X, Y):
    """
    Find all possible Longest Common Subsequences of two sequences.

    This function returns all distinct LCS strings between X and Y.
    Note that there can be multiple LCS with the same length.

    Args:
        X (str or list): First sequence
        Y (str or list): Second sequence

    Returns:
        set: Set of all distinct longest common subsequences

    Example:
        >>> lcs_all_sequences("ABCBDAB", "BDCABA")
        {'BDAB', 'BCBA', 'BCAB'}  # All possible LCS with length 4
    """
    m = len(X)
    n = len(Y)

    # Create a table to store the LCS lengths
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill the dp table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Function to backtrack and find all LCS
    def backtrack(i, j, path):
        if i == 0 or j == 0:
            return ["".join(reversed(path))]

        if X[i-1] == Y[j-1]:
            return backtrack(i-1, j-1, [X[i-1]] + path)

        result = []
        if dp[i][j-1] == dp[i][j]:
            result.extend(backtrack(i, j-1, path))
        if dp[i-1][j] == dp[i][j]:
            result.extend(backtrack(i-1, j, path))

        return result

    # Get all LCS
    all_lcs = set(backtrack(m, n, []))

    return all_lcs

# Example usage
if __name__ == "__main__":
    sequence1 = "ABCBDAB"
    sequence2 = "BDCABA"

    # Find the length of LCS
    length = lcs_length(sequence1, sequence2)
    print(f"Length of LCS: {length}")

    # Find the LCS
    length, subsequence = lcs(sequence1, sequence2)
    print(f"LCS: {subsequence} (length: {length})")

    # Find all possible LCS
    all_subsequences = lcs_all_sequences(sequence1, sequence2)
    print(f"All possible LCS: {all_subsequences}")

    # Example with lists
    list1 = [1, 2, 3, 4, 1]
    list2 = [3, 4, 1, 2, 1, 3]
    length, subsequence = lcs(list1, list2)
    print(f"\nLCS of {list1} and {list2}: {subsequence} (length: {length})")
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
