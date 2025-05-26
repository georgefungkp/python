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