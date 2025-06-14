# Implementation of common sorting algorithms
# This file provides implementations of Quick Sort and Merge Sort algorithms

def quick_sort(arr):
    """
    Implementation of the Quick Sort algorithm using a divide-and-conquer approach.

    Quick Sort works by:  
    1. Selecting a 'pivot' element from the array
    2. Partitioning the array into elements less than pivot, equal to pivot, and greater than pivot
    3. Recursively sorting the sub-arrays

    Time Complexity:
    - Average case: O(n log n)
    - Worst case: O(n²) when the array is already sorted or nearly sorted

    Parameters:
        arr (list): The input array to be sorted

    Returns:
        list: The sorted array
    """
    # Base case: arrays of size 0 or 1 are already sorted
    if len(arr) <= 1:
        return arr

    # Choose the middle element as pivot (other strategies exist)
    pivot = arr[len(arr) // 2]  

    # Partition the array into three parts
    left = [x for x in arr if x < pivot]      # Elements less than pivot
    middle = [x for x in arr if x == pivot]   # Elements equal to pivot
    right = [x for x in arr if x > pivot]     # Elements greater than pivot

    # Recursively sort left and right partitions, then combine
    return quick_sort(left) + middle + quick_sort(right)

# Test case for Quick Sort
arr = [3, 6, 8, 10, 1, 2, 1]
print(quick_sort(arr))  # Output: [1, 1, 2, 3, 6, 8, 10]


def merge_sort(arr):
    """
    Implementation of the Merge Sort algorithm using a divide-and-conquer approach.

    Merge Sort works by:
    1. Dividing the array into two halves
    2. Recursively sorting each half
    3. Merging the sorted halves back together

    Time Complexity: O(n log n) in all cases
    Space Complexity: O(n) for the auxiliary arrays

    Parameters:
        arr (list): The input array to be sorted

    Returns:
        list: The sorted array
    """
    # Helper function to merge two sorted arrays
    def merge(left, right):
        """
        Merges two sorted arrays into a single sorted array.

        Parameters:
            left (list): First sorted array
            right (list): Second sorted array

        Returns:
            list: Merged sorted array
        """
        sorted_arr = []  # Result array
        i = j = 0        # Pointers for left and right arrays

        # Compare elements from both arrays and add the smaller one to result
        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                sorted_arr.append(left[i])
                i += 1
            else:
                sorted_arr.append(right[j])
                j += 1

        # Add any remaining elements from left array
        sorted_arr.extend(left[i:])
        # Add any remaining elements from right array
        sorted_arr.extend(right[j:])

        return sorted_arr

    # Base case: arrays of size 0 or 1 are already sorted
    if len(arr) <= 1:
        return arr

    # Divide the array into two halves
    mid = len(arr) // 2

    # Recursively sort both halves
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    # Merge the sorted halves
    return merge(left, right)

# Test case for Merge Sort
arr = [38, 27, 43, 10]
print(merge_sort(arr))  # Output: [10, 27, 38, 43]