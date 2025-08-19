"""
Maximum Subarray Problem - Comprehensive Implementation

This module contains multiple approaches to solve the maximum subarray sum problem:
1. Kadane's Algorithm (O(n) - optimal)
2. Brute Force approaches (O(n²) and O(n³) - for educational purposes)

The maximum subarray problem asks: given an array of integers, find the contiguous 
subarray with the largest sum.

Example: [-2, 1, -3, 4, -1, 2, 1, -5, 4] → subarray [4, -1, 2, 1] has sum 6
"""


def kadanes_algorithm(arr):
    """
    Finds the maximum contiguous subarray sum using Kadane's Algorithm.

    This is the most efficient solution using dynamic programming.
    Time Complexity: O(n) - linear time
    Space Complexity: O(1) - constant space

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
    Finds maximum subarray sum and its indices using Kadane's Algorithm.
    This extended version tracks the start and end indices of the maximum subarray.

    Time Complexity: O(n) - linear time
    Space Complexity: O(1) - constant space

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
    temp_start = 0  # Temporary start index for the current subarray

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
            start = temp_start  # Update start index from temporary
            end = i  # Update end index to current position

    # Return the indices of the maximum subarray and its sum
    return (start, end, max_global)


def max_subarray_sum(arr):
    """
    Alternative implementation of Kadane's algorithm for finding maximum subarray sum.
    This is a more concise version that achieves the same result.

    Time Complexity: O(n) - linear time
    Space Complexity: O(1) - constant space

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


def max_subarray_sum_kadane(arr):
    """
    Find the maximum subarray sum using Kadane's algorithm with index tracking.

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
    end = 0  # End of maximum subarray
    s = 0  # Start of potential new subarray

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


def max_subarray_sum_brute_force(arr):
    """
    Find the maximum subarray sum using a brute force approach.

    Examines all possible subarrays to find the one with the maximum sum.
    This is the most intuitive but least efficient approach.

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

    Eliminates the innermost loop by computing the sum incrementally.
    This is more efficient than the basic brute force but still not optimal.

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


# Test all algorithms
if __name__ == "__main__":
    test_arrays = [
        [-2, 1, -3, 4, -1, 2, 1, -5, 4],  # Classic example
        [1, 2, 3, -2, 5],  # Mostly positive
        [-1, -2, -3, -4],  # All negative
        [5, 4, -1, 7, 8],  # Mixed values
        [1],  # Single element
        []  # Empty array (edge case)
    ]

    for i, arr in enumerate(test_arrays):
        if not arr:  # Handle empty array
            print(f"\nTest Array {i + 1}: {arr} (empty)")
            print("Empty array - skipping tests")
            continue

        print(f"\nTest Array {i + 1}: {arr}")

        # Using Kadane's algorithm (most efficient)
        max_sum, start, end = max_subarray_sum_kadane(arr)
        print(f"Kadane's Algorithm: Max Sum = {max_sum}, Subarray = {arr[start:end + 1]}")

        # Using better brute force (medium efficiency)
        max_sum, start, end = max_subarray_sum_better(arr)
        print(f"Better Brute Force: Max Sum = {max_sum}, Subarray = {arr[start:end + 1]}")

        # Using simple Kadane's algorithm
        simple_max = max_subarray_sum(arr)
        print(f"Simple Kadane's: Max Sum = {simple_max}")

        # Using original Kadane's implementation
        kadane_max = kadanes_algorithm(arr)
        print(f"Original Kadane's: Max Sum = {kadane_max}")

    # Performance comparison note
    print("\n" + "=" * 60)
    print("ALGORITHM PERFORMANCE COMPARISON:")
    print("=" * 60)
    print("1. Kadane's Algorithm:     O(n) time, O(1) space - OPTIMAL")
    print("2. Better Brute Force:     O(n²) time, O(1) space")
    print("3. Basic Brute Force:      O(n³) time, O(1) space - SLOWEST")
    print("\nRecommendation: Use Kadane's Algorithm for production code!")