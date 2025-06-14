# Edit Distance (Levenshtein Distance) implementation using Dynamic Programming
# The Edit Distance calculates the minimum number of operations (insertions, deletions, or
# substitutions) required to transform one string into another
# Edit Distance (Levenshtein Distance) implementation using Dynamic Programming
# The Edit Distance calculates the minimum number of operations (insertions, deletions, or
# substitutions) required to transform one string into another

def edit_distance(str1, str2):
    """
    Computes the Edit Distance (Levenshtein Distance) between two strings.

    The edit distance is the minimum number of single-character operations (insertions,
    deletions, or substitutions) required to transform one string into another.

    Args:
        str1 (str): First string
        str2 (str): Second string

    Returns:
        int: The minimum number of operations required

    Example:
        >>> edit_distance("kitten", "sitting")
        3  # Replace 'k' with 's', replace 'e' with 'i', insert 'g'
    """
    m = len(str1)
    n = len(str2)

    # Initialize DP table
    # dp[i][j] represents the edit distance between str1[0..i-1] and str2[0..j-1]
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    # Fill the DP table bottom-up
    for i in range(m + 1):
        for j in range(n + 1):
            # If first string is empty, insert all characters of second string
            if i == 0:
                dp[i][j] = j
            # If second string is empty, remove all characters of first string
            elif j == 0:
                dp[i][j] = i
            # If last characters match, ignore the last character and recur for remaining
            elif str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            # If last characters don't match, consider all operations
            # Insert: dp[i][j-1]
            # Remove: dp[i-1][j]
            # Replace: dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i][j-1],      # Insert
                                   dp[i-1][j],      # Remove
                                   dp[i-1][j-1])    # Replace

    return dp[m][n]


def edit_distance_with_operations(str1, str2):
    """
    Computes the Edit Distance between two strings and returns the operations performed.

    Args:
        str1 (str): First string
        str2 (str): Second string

    Returns:
        tuple: (edit_distance, list of operations)

    Example:
        >>> edit_distance_with_operations("kitten", "sitting")
        (3, [('replace', 0, 'k', 's'), ('replace', 4, 'e', 'i'), ('insert', 6, '', 'g')])
    """
    m = len(str1)
    n = len(str2)

    # Initialize DP table
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    # Fill the DP table
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])

    # Backtrack to find the operations
    operations = []
    i, j = m, n

    while i > 0 or j > 0:
        if i > 0 and j > 0 and str1[i-1] == str2[j-1]:
            # Characters match, no operation needed
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j] == dp[i][j-1] + 1):
            # Insert operation
            operations.append(('insert', i, '', str2[j-1]))
            j -= 1
        elif i > 0 and (j == 0 or dp[i][j] == dp[i-1][j] + 1):
            # Delete operation
            operations.append(('delete', i-1, str1[i-1], ''))
            i -= 1
        else:
            # Replace operation
            operations.append(('replace', i-1, str1[i-1], str2[j-1]))
            i -= 1
            j -= 1

    # Reverse to get operations in correct order
    operations.reverse()

    return dp[m][n], operations


# Example usage
if __name__ == "__main__":
    # Example 1: Basic edit distance
    str1 = "kitten"
    str2 = "sitting"

    distance = edit_distance(str1, str2)
    print(f"Edit distance between '{str1}' and '{str2}': {distance}")

    # Example 2: With operations
    distance, operations = edit_distance_with_operations(str1, str2)
    print(f"\nEdit distance: {distance}")
    print("Operations:")
    for op in operations:
        op_type, position, char1, char2 = op
        if op_type == 'insert':
            print(f"  Insert '{char2}' at position {position}")
        elif op_type == 'delete':
            print(f"  Delete '{char1}' at position {position}")
        else:  # replace
            print(f"  Replace '{char1}' with '{char2}' at position {position}")
def edit_distance(str1, str2):
    """
    Computes the Edit Distance (Levenshtein Distance) between two strings.

    The edit distance is the minimum number of single-character operations (insertions,
    deletions, or substitutions) required to transform one string into another.

    Args:
        str1 (str): First string
        str2 (str): Second string

    Returns:
        int: The minimum number of operations required

    Example:
        >>> edit_distance("kitten", "sitting")
        3  # Replace 'k' with 's', replace 'e' with 'i', insert 'g'
    """
    m = len(str1)
    n = len(str2)

    # Initialize DP table
    # dp[i][j] represents the edit distance between str1[0..i-1] and str2[0..j-1]
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    # Fill the DP table bottom-up
    for i in range(m + 1):
        for j in range(n + 1):
            # If first string is empty, insert all characters of second string
            if i == 0:
                dp[i][j] = j
            # If second string is empty, remove all characters of first string
            elif j == 0:
                dp[i][j] = i
            # If last characters match, ignore the last character and recur for remaining
            elif str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            # If last characters don't match, consider all operations
            # Insert: dp[i][j-1]
            # Remove: dp[i-1][j]
            # Replace: dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i][j-1],      # Insert
                                   dp[i-1][j],      # Remove
                                   dp[i-1][j-1])    # Replace

    return dp[m][n]


def edit_distance_with_operations(str1, str2):
    """
    Computes the Edit Distance between two strings and returns the operations performed.

    Args:
        str1 (str): First string
        str2 (str): Second string

    Returns:
        tuple: (edit_distance, list of operations)

    Example:
        >>> edit_distance_with_operations("kitten", "sitting")
        (3, [('replace', 0, 'k', 's'), ('replace', 4, 'e', 'i'), ('insert', 6, '', 'g')])
    """
    m = len(str1)
    n = len(str2)

    # Initialize DP table
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    # Fill the DP table
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])

    # Backtrack to find the operations
    operations = []
    i, j = m, n

    while i > 0 or j > 0:
        if i > 0 and j > 0 and str1[i-1] == str2[j-1]:
            # Characters match, no operation needed
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j] == dp[i][j-1] + 1):
            # Insert operation
            operations.append(('insert', i, '', str2[j-1]))
            j -= 1
        elif i > 0 and (j == 0 or dp[i][j] == dp[i-1][j] + 1):
            # Delete operation
            operations.append(('delete', i-1, str1[i-1], ''))
            i -= 1
        else:
            # Replace operation
            operations.append(('replace', i-1, str1[i-1], str2[j-1]))
            i -= 1
            j -= 1

    # Reverse to get operations in correct order
    operations.reverse()

    return dp[m][n], operations


# Example usage
if __name__ == "__main__":
    # Example 1: Basic edit distance
    str1 = "kitten"
    str2 = "sitting"

    distance = edit_distance(str1, str2)
    print(f"Edit distance between '{str1}' and '{str2}': {distance}")

    # Example 2: With operations
    distance, operations = edit_distance_with_operations(str1, str2)
    print(f"\nEdit distance: {distance}")
    print("Operations:")
    for op in operations:
        op_type, position, char1, char2 = op
        if op_type == 'insert':
            print(f"  Insert '{char2}' at position {position}")
        elif op_type == 'delete':
            print(f"  Delete '{char1}' at position {position}")
        else:  # replace
            print(f"  Replace '{char1}' with '{char2}' at position {position}")
