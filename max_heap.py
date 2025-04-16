# Consider two arrays of integers, playground[n] and b[n]. What is the maximum number of pairs that can be formed where playground[i]> b[j]? Each element can be in no more than one pair.
# Find the maximum number of such possible pairs.
# Example
# n = 3
# playground = [1, 2, 3]
# b = [1, 2, 1]
# Two ways the maximum number of pairs can be selected:

# {playground[1], b[0]}={2, 1} and {playground[2], b[2]}={3, 1} are valid pairs.
# {playground[1], b[0]}={2, 1} and {playground[2], b[1]}={3, 2} are valid pairs.
# No more than 2 pairs can be formed, so return 2.
# Function Description
# Complete the function findNumOfPairs in the editor below.
# findNumOfPairs has the following parameters:
# int playground[n]: an array of integers
# int b[n]: an array of integers
# Returns
# int: the maximum number of pairs possible
# Constraints
# • 1≤ n ≤105
# • 1 ≤ playground[i] ≤ 109


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


a1 = [5, 3, 9, 7, 6]
b1 = [2, 8, 1, 4, 3]
# Output: 4

a2 = [10, 20, 30, 40]
b2 = [15, 25, 35, 45]
# Output: 2

a3 = [1, 2, 3, 4, 5, 6]
b3 = [6, 5, 4, 3, 2, 1]
# Output: 3

a4 = [11, 13, 15, 17, 19, 21, 23]
b4 = [10, 12, 14, 16, 18, 20, 22]
# Output: 7

a5 = [1, 1, 1]
b5 = [2, 2, 2]
# Output: 0

A = [a1, a2, a3, a4, a5]
B = [b1, b2, b3, b4, b5]

for a, b in zip(A, B):
    print(findNumOfPairs(a,b))


