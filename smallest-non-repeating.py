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


# Example usage
# arr = [1, 2, 3, 4, 1, 3]
arr = [4, 5, 1, 2, 0, 4, 5, 1, 2, 0, 0, 2]
print(min_length_non_repeating_subarray(arr))  # Output: 5
