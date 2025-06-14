# Problem: Maximum Number of Valid Pairs
#
# Problem Statement:
# Consider two arrays of integers, A[n] and B[n]. What is the maximum number of pairs that can be formed
# where A[i] > B[j]? Each element can be in no more than one pair.
# Find the maximum number of such possible pairs.
#
# Example:
# n = 3
# A = [1, 2, 3]
# B = [1, 2, 1]
# Two ways the maximum number of pairs can be selected:
# {A[1], B[0]}={2, 1} and {A[2], B[2]}={3, 1} are valid pairs.
# {A[1], B[0]}={2, 1} and {A[2], B[1]}={3, 2} are valid pairs.
# No more than 2 pairs can be formed, so return 2.
#
# Function Description:
# Complete the function findNumOfPairs in the editor below.
# findNumOfPairs has the following parameters:
#   int A[n]: an array of integers
#   int B[n]: an array of integers
# 
# Returns:
#   int: the maximum number of pairs possible
#
# Constraints:
# • 1≤ n ≤10^5
# • 1 ≤ A[i] ≤ 10^9


# def findNumOfPairs(playground, b):
#     new_a = sorted(playground)
#     new_b = sorted(b)
#     valid_pairs = 0
#     i = j = 0
#     while i < len(new_a):
#         if new_a[i] > new_b[j]:
#             valid_pairs += 1
#             i += 1
#             j += 1
#         else:
#             i += 1
#         # if new_a[i] < new_b[i]:
#         #     return valid_pairs
#
#     return valid_pairs


def findNumOfPairs(A, B):
    import heapq
    # Initializing the max-heap for the array A[]
    pq1 = []
    pq2 = []
    N = len(a)

    # Adding the values of A[] into max heap
    for i in range(N):
        heapq.heappush(pq1, -A[i])

        # Adding the values of B[] into max heap
    for i in range(N):
        heapq.heappush(pq2, -B[i])

        # Counter variable
    c = 0

    # Loop to iterate through the heap
    for i in range(N):

        # Comparing the values at the top.
        # If the value of heap A[] is greater,
        # then counter is incremented
        if -pq1[0] > -pq2[0]:
            c += 1
            heapq.heappop(pq1)
            heapq.heappop(pq2)

        else:
            if len(pq2) == 0:
                break
            heapq.heappop(pq2)
    return (c)


# Test Case 1: Mix of values where some elements from A are greater than some in B
a1 = [5, 3, 9, 7, 6]  # Array A
b1 = [2, 8, 1, 4, 3]  # Array B
# Expected Output: 4 (Can form 4 valid pairs)

# Test Case 2: Each element in A is less than corresponding element in B, except in some positions
a2 = [10, 20, 30, 40]  # Array A
b2 = [15, 25, 35, 45]  # Array B
# Expected Output: 2 (Can form 2 valid pairs)

# Test Case 3: A is sorted ascending, B is sorted descending
a3 = [1, 2, 3, 4, 5, 6]  # Array A
b3 = [6, 5, 4, 3, 2, 1]  # Array B
# Expected Output: 3 (Can form 3 valid pairs)

# Test Case 4: All elements in A are greater than all corresponding elements in B
a4 = [11, 13, 15, 17, 19, 21, 23]  # Array A
b4 = [10, 12, 14, 16, 18, 20, 22]  # Array B
# Expected Output: 7 (Can form 7 valid pairs - every element can be paired)

# Test Case 5: All elements in A are less than all elements in B (no valid pairs possible)
a5 = [1, 1, 1]  # Array A
b5 = [2, 2, 2]  # Array B
# Expected Output: 0 (Cannot form any valid pairs)

# Combine all test cases into arrays
A = [a1, a2, a3, a4, a5]
B = [b1, b2, b3, b4, b5]

# Run the function on each test case and print results
for a, b in zip(A, B):
    print(findNumOfPairs(a,b))


