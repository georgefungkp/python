def min_length_non_repeating_subarray(arr):
    n = len(arr)
    if n == 0:
        return 0

    # Dictionary to store the last occurrence of each element
    last_occurrence = {}
    min_length = float('inf')
    start = 0

    for end in range(n):
        if arr[end] in last_occurrence:
            start = max(start, last_occurrence[arr[end]] + 1)
            min_length = min(min_length, end - start + 1)
        last_occurrence[arr[end]] = end

    return min_length if min_length != float('inf') else 0
# Smallest Non-Repeating Character Finder
# This program finds the first non-repeating character in a string

def first_non_repeating_char(s):
    """
    Find the first non-repeating character in a string and return its index.

    Time Complexity: O(n) where n is the length of the string
    Space Complexity: O(k) where k is the size of the character set (constant for ASCII)

    Parameters:
        s (str): The input string to analyze

    Returns:
        int: The index of the first non-repeating character, or -1 if none exists
    """
    # Create a dictionary to count character occurrences
    char_count = {}

    # First pass: count occurrences of each character
    for char in s:
        if char in char_count:
            char_count[char] += 1
        else:
            char_count[char] = 1

    # Second pass: find the first character with count 1
    for i, char in enumerate(s):
        if char_count[char] == 1:
            return i

    # If no non-repeating character is found
    return -1


def first_non_repeating_char_optimized(s):
    """
    Optimized version that uses a single pass with a different data structure.

    Time Complexity: O(n) where n is the length of the string
    Space Complexity: O(k) where k is the size of the character set

    Parameters:
        s (str): The input string to analyze

    Returns:
        int: The index of the first non-repeating character, or -1 if none exists
    """
    # Dictionary to store both count and first position
    char_info = {}

    # Single pass through the string
    for i, char in enumerate(s):
        if char not in char_info:
            # Store (count, first_position)
            char_info[char] = [1, i]
        else:
            # Increment count, keep position
            char_info[char][0] += 1

    # Find the character with count 1 and the smallest position
    result = float('inf')  # Initialize to infinity
    for count, pos in char_info.values():
        if count == 1 and pos < result:
            result = pos

    # Return result or -1 if no non-repeating character
    return result if result != float('inf') else -1


# Test the functions
if __name__ == "__main__":
    test_strings = [
        "abcdefg",          # All unique characters
        "aabbccddeeffgg",   # All repeating characters
        "abcdefgabcdefg",   # All characters repeat once
        "aabccddeeff",      # Only 'b' appears once
        "stress",           # 't' is the first non-repeating character
        ""                  # Empty string
    ]

    print("Testing First Non-Repeating Character Functions:\n")

    for i, test in enumerate(test_strings):
        print(f"Test {i+1}: '{test}'")

        # Regular version
        result1 = first_non_repeating_char(test)
        if result1 != -1:
            print(f"  Regular: Character '{test[result1]}' at index {result1}")
        else:
            print("  Regular: No non-repeating character found")

        # Optimized version
        result2 = first_non_repeating_char_optimized(test)
        if result2 != -1:
            print(f"  Optimized: Character '{test[result2]}' at index {result2}")
        else:
            print("  Optimized: No non-repeating character found")

        print()

# Example usage
# arr = [1, 2, 3, 4, 1, 3]
arr = [4, 5, 1, 2, 0, 4, 5, 1, 2, 0, 0, 2]
print(min_length_non_repeating_subarray(arr))  # Output: 5
