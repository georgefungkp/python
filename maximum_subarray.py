    # Implementation of Kadane's Algorithm for maximum subarray sum problem
    # Time Complexity: O(n) where n is the length of the array
    # Space Complexity: O(1) as we only use a constant amount of extra space

def kadanes_algorithm(arr):
    """
    Finds the maximum contiguous subarray sum using Kadane's Algorithm

    Args:
    arr (list): List of numbers

    Returns:
    int: Maximum subarray sum
    """
    # Handle empty array case
    if not arr:
        return 0

    # Initialize variables with the first element
    max_current = max_global = arr[0]

    # Iterate through the rest of the array
    for num in arr[1:]:
        # Decide whether to add to current subarray or start new
        # max_current represents the maximum sum ending at the current position
        max_current = max(num, max_current + num)

        # Update global maximum if needed
        # max_global represents the maximum sum found so far
        if max_current > max_global:
            max_global = max_current

    return max_global


def kadanes_algorithm_with_indices(arr):
    """
    Finds maximum subarray sum and its indices using Kadane's Algorithm
    This extended version tracks the start and end indices of the maximum subarray

    Args:
    arr (list): List of numbers

    Returns:
    tuple: (start_index, end_index, max_sum)
    """
    # Handle empty array case
    if not arr:
        return (0, 0, 0)

    # Initialize variables with the first element
    max_current = max_global = arr[0]
    start = end = 0  # Final result indices
    temp_start = 0   # Temporary start index for the current subarray

    # Iterate through the rest of the array
    for i in range(1, len(arr)):
        # Decide whether to start a new subarray or extend the existing one
        if arr[i] > max_current + arr[i]:
            # Start a new subarray from current position
            max_current = arr[i]
            temp_start = i  # Update temporary start index
        else:
            # Extend the existing subarray
            max_current += arr[i]

        # Update global maximum and indices if needed
        if max_current > max_global:
            max_global = max_current  # Update max sum
            start = temp_start        # Update start index from temporary
            end = i                   # Update end index to current position

    # Return the indices of the maximum subarray and its sum
    return (start, end, max_global)


def max_subarray_sum(arr):
    """
    Alternative implementation of Kadane's algorithm for finding maximum subarray sum
    This is a more concise version that achieves the same result

    Args:
    arr (list): List of numbers

    Returns:
    int: Maximum subarray sum
    """
    # Initialize result with first element
    res = arr[0]
    # Initialize running sum
    total = 0

    for num in arr:
        # Add current element to running sum
        total = total + num
        # Update result if current running sum is greater
        res = max(res, total)
        # Reset running sum to 0 if it becomes negative
        # This effectively starts a new subarray
        total = max(total, 0)

    return res