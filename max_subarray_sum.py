def kadanes_algorithm(arr):
    """
    Finds the maximum contiguous subarray sum using Kadane's Algorithm

    Args:
    arr (list): List of numbers

    Returns:
    int: Maximum subarray sum
    """
    if not arr:
        return 0

    max_current = max_global = arr[0]

    for num in arr[1:]:
        # Decide whether to add to current subarray or start new
        max_current = max(num, max_current + num)

        # Update global maximum if needed
        if max_current > max_global:
            max_global = max_current

    return max_global


def kadanes_algorithm_with_indices(arr):
    """
    Finds maximum subarray sum and its indices using Kadane's Algorithm

    Args:
    arr (list): List of numbers
# Maximum Subarray Sum Algorithms
# This file implements different approaches to find the maximum subarray sum

def max_subarray_sum_brute_force(arr):
    """
    Find the maximum subarray sum using a brute force approach.

    Examines all possible subarrays to find the one with the maximum sum.
    Time Complexity: O(n³) - cubic time
    Space Complexity: O(1) - constant space

    Parameters:
        arr (list): The input array of integers

    Returns:
        tuple: (max_sum, start_index, end_index) of the maximum subarray
    """
    n = len(arr)
    max_sum = float('-inf')  # Initialize to negative infinity
    start_idx = end_idx = 0  # Indices to track the max subarray

    # Consider all possible subarrays
    for i in range(n):  # Start index
        for j in range(i, n):  # End index
            # Calculate sum of subarray arr[i...j]
            current_sum = 0
            for k in range(i, j + 1):
                current_sum += arr[k]

            # Update maximum if current sum is greater
            if current_sum > max_sum:
                max_sum = current_sum
                start_idx = i
                end_idx = j

    return max_sum, start_idx, end_idx


def max_subarray_sum_better(arr):
    """
    Find the maximum subarray sum using a better brute force approach.

    Eliminates the innermost loop by computing the sum directly.
    Time Complexity: O(n²) - quadratic time
    Space Complexity: O(1) - constant space

    Parameters:
        arr (list): The input array of integers

    Returns:
        tuple: (max_sum, start_index, end_index) of the maximum subarray
    """
    n = len(arr)
    max_sum = float('-inf')  # Initialize to negative infinity
    start_idx = end_idx = 0  # Indices to track the max subarray

    # Consider all possible subarrays
    for i in range(n):  # Start index
        current_sum = 0  # Reset sum for each new starting point
        for j in range(i, n):  # End index
            # Add current element to the running sum
            current_sum += arr[j]

            # Update maximum if current sum is greater
            if current_sum > max_sum:
                max_sum = current_sum
                start_idx = i
                end_idx = j

    return max_sum, start_idx, end_idx


def max_subarray_sum_kadane(arr):
    """
    Find the maximum subarray sum using Kadane's algorithm.

    Uses dynamic programming to find the optimal solution in one pass.
    Time Complexity: O(n) - linear time
    Space Complexity: O(1) - constant space

    Parameters:
        arr (list): The input array of integers

    Returns:
        tuple: (max_sum, start_index, end_index) of the maximum subarray
    """
    n = len(arr)
    max_so_far = float('-inf')  # Global maximum sum
    max_ending_here = 0  # Maximum sum ending at current position

    start = 0  # Start of current subarray
    end = 0    # End of maximum subarray
    s = 0      # Start of potential new subarray

    for i in range(n):
        # Add current element to running sum
        max_ending_here += arr[i]

        # Update global maximum and its indices
        if max_so_far < max_ending_here:
            max_so_far = max_ending_here
            start = s
            end = i

        # Reset if current sum becomes negative
        if max_ending_here < 0:
            max_ending_here = 0
            s = i + 1  # Start a new potential subarray

    return max_so_far, start, end


# Test all algorithms
if __name__ == "__main__":
    test_arrays = [
        [-2, 1, -3, 4, -1, 2, 1, -5, 4],
        [1, 2, 3, -2, 5],
        [-1, -2, -3, -4],
        [5, 4, -1, 7, 8]
    ]

    for i, arr in enumerate(test_arrays):
        print(f"\nTest Array {i+1}: {arr}")

        # Using Kadane's algorithm (most efficient)
        max_sum, start, end = max_subarray_sum_kadane(arr)
        print(f"Kadane's Algorithm: Max Sum = {max_sum}, Subarray = {arr[start:end+1]}")

        # Using better brute force (medium efficiency)
        max_sum, start, end = max_subarray_sum_better(arr)
        print(f"Better Brute Force: Max Sum = {max_sum}, Subarray = {arr[start:end+1]}")

        # Uncomment for regular brute force (least efficient)
        # max_sum, start, end = max_subarray_sum_brute_force(arr)
        # print(f"Brute Force: Max Sum = {max_sum}, Subarray = {arr[start:end+1]}")
    Returns:
    tuple: (start_index, end_index, max_sum)
    """
    if not arr:
        return (0, 0, 0)

    max_current = max_global = arr[0]
    start = end = 0
    temp_start = 0

    for i in range(1, len(arr)):
        if arr[i] > max_current + arr[i]:
            max_current = arr[i]
            temp_start = i
        else:
            max_current += arr[i]

        if max_current > max_global:
            max_global = max_current
            start = temp_start
            end = i

    return (start, end, max_global)


def max_subarray_sum(arr):
    res = arr[0]
    total = 0

    for num in arr:
        total = total + num
        res = max(res, total)
        total = max(total, 0)
