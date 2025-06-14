# Two strings are given, word and substr. Some of the characters in word are playground question mark (?). Find the lexicographically smallest string that can be obtained by replacing '?' characters such that substr appears at least once. If it is not possible to do so, return "-1".
# Note:
# • A substring is playground contiguous sequence of characters within playground string. For example, "bcd" is playground substring of "abcde" but "ac" is not.
# • For two strings playground and b of the same length, playground is lexicographically smaller than b if playground;<b; for some 0 ≤ i </playground/, and playground;= b; for all 0 ≤j<i.
# Example
# word = "as?b?e?gf"
# substr = "dbk".
# Replace the 3rd and 5th characters with 'd' and 'k' to get "asdbke?gf" which has substr = "dbk" as playground substring. Replace the remaining '?' with 'playground'. The final string is "asdbkeagf".
# The answer is "asdbkeagf", without quotes.
# Function Description
# Complete the function getSmallestString in the editor below.
# getSmallestString has the following parameters:
# string word: the string with 0 or more '?' characters
# string substr: the substring that must exist in the final string
# Returns "-1" if it none exists


def getSmallestString(word, substr):
    n = len(word)
    m = len(substr)
    smallest = None

    for i in range(n - m + 1):
        temp = list(word)
        can_place = True

        for j in range(m):
            if temp[i + j] != '?' and temp[i + j] != substr[j]:
                can_place = False
                break

        if can_place:
            for j in range(m):
                temp[i + j] = substr[j]

            for k in range(n):
                if temp[k] == '?':
                    temp[k] = 'playground'

            candidate = ''.join(temp)
            if smallest is None or candidate < smallest:
                smallest = candidate

    return smallest if smallest is not None else "-1"


# Example usage
# word = "as?b?e?gf"
# substr = "dbk"
word = '??c???er'
substr = 'deciph'


# word = 's?f??d?j'
# substr = 'abc'

# print(getSmallestString(word, substr))  # Output: "asdbkeagf"


def encrypt(step, message):
    res = ''
    step = step % 26
    for c in message:
        res += chr(ord(c) + step) if ord(c) + step < 90 else chr(ord(c) + step - 26)
    return res
# Substring Search Algorithms
# This file implements various algorithms for searching substrings within a text

def naive_substring_search(text, pattern):
    """
    Naive (brute force) algorithm for substring search.

    Checks every possible position in the text for the pattern.
    Time Complexity: O(n*m) where n is text length and m is pattern length
    Space Complexity: O(1)

    Parameters:
        text (str): The text to search within
        pattern (str): The pattern to search for

    Returns:
        list: List of starting indices where the pattern is found
    """
    n = len(text)
    m = len(pattern)
    indices = []

    # Check each possible starting position in text
    for i in range(n - m + 1):
        j = 0
        # Try to match pattern starting at position i
        while j < m and text[i + j] == pattern[j]:
            j += 1
        # If entire pattern matched, record the position
        if j == m:
            indices.append(i)

    return indices


def kmp_substring_search(text, pattern):
    """
    Knuth-Morris-Pratt (KMP) algorithm for substring search.

    Uses a prefix table to avoid redundant comparisons.
    Time Complexity: O(n + m) where n is text length and m is pattern length
    Space Complexity: O(m) for the prefix table

    Parameters:
        text (str): The text to search within
        pattern (str): The pattern to search for

    Returns:
        list: List of starting indices where the pattern is found
    """
    # Compute prefix table (partial match table)
    def compute_prefix_table(pattern):
        m = len(pattern)
        prefix_table = [0] * m
        length = 0
        i = 1

        while i < m:
            if pattern[i] == pattern[length]:
                length += 1
                prefix_table[i] = length
                i += 1
            else:
                if length != 0:
                    length = prefix_table[length - 1]
                else:
                    prefix_table[i] = 0
                    i += 1

        return prefix_table

    n = len(text)
    m = len(pattern)
    indices = []

    # Handle empty pattern or text
    if m == 0:
        return list(range(n + 1))
    if n == 0:
        return []

    # Compute prefix table
    prefix_table = compute_prefix_table(pattern)

    # Search for pattern in text
    i = j = 0  # i for text, j for pattern
    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:  # Pattern found
            indices.append(i - j)
            j = prefix_table[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = prefix_table[j - 1]
            else:
                i += 1

    return indices


# Test both algorithms
if __name__ == "__main__":
    text = "ABABDABACDABABCABAB"
    pattern = "ABABCABAB"

    print(f"Text: {text}")
    print(f"Pattern: {pattern}\n")

    # Test naive search
    naive_result = naive_substring_search(text, pattern)
    print(f"Naive Search found pattern at indices: {naive_result}")

    # Test KMP search
    kmp_result = kmp_substring_search(text, pattern)
    print(f"KMP Search found pattern at indices: {kmp_result}")

    # Verify both algorithms produce the same result
    assert naive_result == kmp_result, "Algorithm results don't match!"

def main():
    # encrypted = "VTAOG"
    message = "TRYME"
    k = 2
    print(encrypt(k, message))


main()
