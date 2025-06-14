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
# Max Heap Implementation
# A max heap is a complete binary tree where the value of each node is greater than
# or equal to the values of its children.

class MaxHeap:
    """
    A Max Heap implementation with basic operations.

    In a max heap, for any given node i, the value of i is greater than or equal to 
    the values of its children, and the highest value element is at the root.

    This implementation uses a zero-based array to represent the heap, where:
    - For any element at index i, its left child is at index 2*i + 1
    - For any element at index i, its right child is at index 2*i + 2
    - For any element at index i, its parent is at index floor((i-1)/2)
    """

    def __init__(self, array=None):
        """
        Initialize a max heap, optionally from an existing array.

        Args:
            array (list, optional): Initial array to heapify. If None, starts with empty heap.
        """
        self.heap = []
        if array:
            self.heap = array.copy()
            self._build_max_heap()

    def __len__(self):
        """
        Return the number of elements in the heap.

        Returns:
            int: Number of elements in the heap.
        """
        return len(self.heap)

    def __str__(self):
        """
        Return a string representation of the heap.

        Returns:
            str: String representation of the heap array.
        """
        return str(self.heap)

    def _parent(self, i):
        """
        Get the parent index of the element at index i.

        Args:
            i (int): Index of the element

        Returns:
            int: Index of the parent element
        """
        return (i - 1) // 2

    def _left_child(self, i):
        """
        Get the left child index of the element at index i.

        Args:
            i (int): Index of the element
# Implementation of Max Heap data structure

class MaxHeap:
    """
    A Max Heap implementation.

    A max heap is a complete binary tree where the value of each node is greater
    than or equal to the values of its children (if they exist).

    Time Complexities:
    - Insert: O(log n)
    - Extract Max: O(log n)
    - Peek Max: O(1)
    - Heapify: O(n)

    Space Complexity: O(n)
    """

    def __init__(self, array=None):
        """
        Initialize a new MaxHeap.

        Args:
            array (list, optional): Initial array to be converted to a max heap.
        """
        self.heap = []
        if array:
            self.heap = array.copy()
            self._heapify()

    def _heapify(self):
        """
        Convert the array into a max heap in-place.
        This method builds the heap from the bottom up.
        """
        n = len(self.heap)
        # Start from the last non-leaf node and heapify each node
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(i)

    def _parent(self, i):
        """
        Get the parent index of the node at index i.

        Args:
            i (int): Index of the current node.

        Returns:
            int: Index of the parent node.
        """
        return (i - 1) // 2

    def _left_child(self, i):
        """
        Get the left child index of the node at index i.

        Args:
            i (int): Index of the current node.

        Returns:
            int: Index of the left child node.
        """
        return 2 * i + 1

    def _right_child(self, i):
        """
        Get the right child index of the node at index i.

        Args:
            i (int): Index of the current node.

        Returns:
            int: Index of the right child node.
        """
        return 2 * i + 2

    def _swap(self, i, j):
        """
        Swap the elements at indices i and j in the heap.

        Args:
            i (int): First index.
            j (int): Second index.
        """
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _sift_up(self, i):
        """
        Move the element at index i up to maintain the max heap property.

        Args:
            i (int): Index of the element to sift up.
        """
        parent = self._parent(i)
        if i > 0 and self.heap[i] > self.heap[parent]:
            self._swap(i, parent)
            self._sift_up(parent)

    def _sift_down(self, i):
        """
        Move the element at index i down to maintain the max heap property.

        Args:
            i (int): Index of the element to sift down.
        """
        max_index = i
        left = self._left_child(i)
        right = self._right_child(i)
        n = len(self.heap)

        # Find the largest among node i and its children
        if left < n and self.heap[left] > self.heap[max_index]:
            max_index = left

        if right < n and self.heap[right] > self.heap[max_index]:
            max_index = right

        # If largest is not the current node, swap and continue sifting down
        if max_index != i:
            self._swap(i, max_index)
            self._sift_down(max_index)

    def insert(self, value):
        """
        Insert a new value into the heap.

        Args:
            value: The value to be inserted.
        """
        self.heap.append(value)
        self._sift_up(len(self.heap) - 1)
# Max Heap Implementation

class MaxHeap:
    """
    A max heap implementation where the largest element is always at the root.

    This data structure supports operations such as insertion, extraction of maximum,
    and peeking at the maximum element with efficient time complexities.

    Attributes:
        heap (list): The list used to store the heap elements.
    """

    def __init__(self, items=None):
        """
        Initialize a new max heap, optionally with initial items.

        Args:
            items (list, optional): Initial items to add to the heap. Defaults to None.
        """
        self.heap = []
        if items:
            for item in items:
                self.insert(item)

    def parent(self, i):
        """
        Get the parent index of a node.

        Args:
            i (int): The index of the node.

        Returns:
            int: The index of the parent node.
        """
        return (i - 1) // 2

    def left_child(self, i):
        """
        Get the left child index of a node.

        Args:
            i (int): The index of the node.

        Returns:
            int: The index of the left child node.
        """
        return 2 * i + 1

    def right_child(self, i):
        """
        Get the right child index of a node.

        Args:
            i (int): The index of the node.

        Returns:
            int: The index of the right child node.
        """
        return 2 * i + 2

    def swap(self, i, j):
        """
        Swap two elements in the heap.

        Args:
            i (int): Index of the first element.
            j (int): Index of the second element.
        """
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def sift_up(self, i):
        """
        Move an element up the heap to maintain the max heap property.

        Args:
            i (int): The index of the element to sift up.
        """
        parent_idx = self.parent(i)
        if i > 0 and self.heap[i] > self.heap[parent_idx]:
            self.swap(i, parent_idx)
            self.sift_up(parent_idx)

    def sift_down(self, i):
        """
        Move an element down the heap to maintain the max heap property.

        Args:
            i (int): The index of the element to sift down.
        """
        max_idx = i
        left_idx = self.left_child(i)
        right_idx = self.right_child(i)

        # Find the largest among the node and its children
        if left_idx < len(self.heap) and self.heap[left_idx] > self.heap[max_idx]:
            max_idx = left_idx

        if right_idx < len(self.heap) and self.heap[right_idx] > self.heap[max_idx]:
            max_idx = right_idx

        # If the largest is not the current node, swap and continue sifting down
        if max_idx != i:
            self.swap(i, max_idx)
            self.sift_down(max_idx)

    def insert(self, item):
        """
        Insert a new item into the heap.

        Args:
            item: The item to insert.

        Returns:
            None
        """
        self.heap.append(item)
        self.sift_up(len(self.heap) - 1)

    def extract_max(self):
        """
        Extract and return the maximum element from the heap.

        Returns:
            The maximum element in the heap, or None if the heap is empty.

        Raises:
            IndexError: If the heap is empty.
        """
        if not self.heap:
            raise IndexError("Heap is empty")

        max_item = self.heap[0]

        # Replace the root with the last element and remove the last element
        last_item = self.heap.pop()

        if self.heap:  # If there are still elements in the heap
            self.heap[0] = last_item
            self.sift_down(0)

        return max_item

    def peek(self):
        """
        Look at the maximum element without removing it.

        Returns:
            The maximum element in the heap, or None if the heap is empty.

        Raises:
            IndexError: If the heap is empty.
        """
        if not self.heap:
            raise IndexError("Heap is empty")
        return self.heap[0]

    def size(self):
        """
        Get the number of elements in the heap.

        Returns:
            int: The number of elements in the heap.
        """
        return len(self.heap)

    def is_empty(self):
        """
        Check if the heap is empty.

        Returns:
            bool: True if the heap is empty, False otherwise.
        """
        return len(self.heap) == 0

    def heapify(self, items):
        """
        Build a max heap from a list of items in O(n) time.

        Args:
            items (list): The list of items to build the heap from.

        Returns:
            None
        """
        self.heap = items.copy()
        # Start from the last non-leaf node and sift down each node
        for i in range(len(self.heap) // 2 - 1, -1, -1):
            self.sift_down(i)

# Example usage
if __name__ == "__main__":
    # Create a max heap
    max_heap = MaxHeap()

    # Insert elements
    elements = [4, 10, 3, 5, 1]
    for element in elements:
        max_heap.insert(element)
        print(f"Inserted {element}, Heap: {max_heap.heap}")

    # Extract elements in order
    print("\nExtracting elements:")
    while not max_heap.is_empty():
        max_elem = max_heap.extract_max()
        print(f"Extracted {max_elem}, Heap: {max_heap.heap}")

    # Demonstrate heapify
    print("\nHeapify example:")
    unsorted_list = [7, 2, 9, 4, 1, 8, 3]
    heap = MaxHeap()
    heap.heapify(unsorted_list)
    print(f"Original list: {unsorted_list}")
    print(f"Heapified: {heap.heap}")

    # Sort using the heap
    sorted_list = []
    while not heap.is_empty():
        sorted_list.append(heap.extract_max())
    print(f"Sorted (descending): {sorted_list}")
    def extract_max(self):
        """
        Remove and return the maximum element from the heap.

        Returns:
            The maximum value in the heap.

        Raises:
            IndexError: If the heap is empty.
        """
        if not self.heap:
            raise IndexError("Extract max from an empty heap")

        max_value = self.heap[0]
        last_value = self.heap.pop()

        if self.heap:  # If the heap still has elements
            self.heap[0] = last_value
            self._sift_down(0)

        return max_value

    def peek(self):
        """
        Return the maximum element without removing it.

        Returns:
            The maximum value in the heap.

        Raises:
            IndexError: If the heap is empty.
        """
        if not self.heap:
            raise IndexError("Peek from an empty heap")

        return self.heap[0]

    def size(self):
        """
        Return the number of elements in the heap.

        Returns:
            int: The size of the heap.
        """
        return len(self.heap)

    def is_empty(self):
        """
        Check if the heap is empty.

        Returns:
            bool: True if the heap is empty, False otherwise.
        """
        return len(self.heap) == 0


def main():
    # Example usage
    print("Creating a max heap from an array:")
    array = [3, 1, 6, 5, 2, 4]
    max_heap = MaxHeap(array)
    print(f"Initial array: {array}")
    print(f"Max heap: {max_heap.heap}")

    print("\nInserting value 9:")
    max_heap.insert(9)
    print(f"Max heap after insertion: {max_heap.heap}")

    print("\nExtracting max elements:")
    while not max_heap.is_empty():
        max_value = max_heap.extract_max()
        print(f"Extracted: {max_value}, Remaining heap: {max_heap.heap}")

    print("\nBuilding a heap with individual insertions:")
    max_heap2 = MaxHeap()
    for num in [7, 3, 8, 1, 5, 2, 6, 4]:
        max_heap2.insert(num)
        print(f"After inserting {num}: {max_heap2.heap}")

    print(f"\nFinal heap size: {max_heap2.size()}")
    print(f"Max value (peek): {max_heap2.peek()}")


if __name__ == "__main__":
    main()
        Returns:
            int: Index of the left child
        """
        return 2 * i + 1

    def _right_child(self, i):
        """
        Get the right child index of the element at index i.

        Args:
            i (int): Index of the element

        Returns:
            int: Index of the right child
        """
        return 2 * i + 2

    def _swap(self, i, j):
        """
        Swap elements at indices i and j.

        Args:
            i (int): First index
            j (int): Second index
        """
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _sift_up(self, i):
        """
        Move the element at index i up to its correct position.

        Args:
            i (int): Index of the element to sift up
        """
        parent = self._parent(i)
        if i > 0 and self.heap[parent] < self.heap[i]:
            self._swap(i, parent)
            self._sift_up(parent)

    def _sift_down(self, i):
        """
        Move the element at index i down to its correct position.

        Args:
            i (int): Index of the element to sift down
        """
        max_index = i
        left = self._left_child(i)
        right = self._right_child(i)

        # Find the largest among node i and its children
        if left < len(self.heap) and self.heap[left] > self.heap[max_index]:
            max_index = left

        if right < len(self.heap) and self.heap[right] > self.heap[max_index]:
            max_index = right

        # If i is not the largest, swap with the largest and continue sifting down
        if i != max_index:
            self._swap(i, max_index)
            self._sift_down(max_index)

    def _build_max_heap(self):
        """
        Build a max heap from the current array in O(n) time.
        """
        # Start from the last non-leaf node and sift down each node
        for i in range(len(self.heap) // 2 - 1, -1, -1):
            self._sift_down(i)

    def get_max(self):
        """
        Get the maximum element (root) from the heap without removing it.

        Returns:
            The maximum element, or None if the heap is empty.
        """
        if len(self.heap) > 0:
            return self.heap[0]
        return None

    def extract_max(self):
        """
        Remove and return the maximum element from the heap.

        Returns:
            The maximum element, or None if the heap is empty.
        """
        if len(self.heap) == 0:
            return None

        # Store the max value to return
        max_val = self.heap[0]

        # Replace the root with the last element and remove the last
        self.heap[0] = self.heap[-1]
        self.heap.pop()

        # Restore heap property
        if len(self.heap) > 0:
            self._sift_down(0)

        return max_val

    def insert(self, key):
        """
        Insert a new key into the heap.

        Args:
            key: The key to insert
        """
        # Add the key to the end of the heap
        self.heap.append(key)

        # Sift up the newly added key to maintain heap property
        self._sift_up(len(self.heap) - 1)

    def increase_key(self, i, key):
        """
        Increase the value of the element at index i to the new key.

        Args:
            i (int): Index of the element to increase
            key: New key value (must be greater than current key)

        Raises:
            ValueError: If new key is smaller than current key
        """
        if i < 0 or i >= len(self.heap):
            raise IndexError("Index out of range")

        if key < self.heap[i]:
            raise ValueError("New key is smaller than current key")

        self.heap[i] = key
        self._sift_up(i)

# Example usage
if __name__ == "__main__":
    # Create a max heap from an array
    arr = [4, 10, 3, 5, 1]
    max_heap = MaxHeap(arr)
    print(f"Initial max heap: {max_heap}")

    # Insert a new element
    max_heap.insert(15)
    print(f"After inserting 15: {max_heap}")

    # Get max without removing
    print(f"Maximum element: {max_heap.get_max()}")

    # Extract max elements one by one
    print("Extracting elements in descending order:")
    while len(max_heap) > 0:
        print(max_heap.extract_max(), end=" ")
    print()

    # Build a priority queue using the max heap
    priority_queue = MaxHeap()
    tasks = [(5, "Low priority task"), (10, "Medium priority task"), (15, "High priority task")]

    # Insert tasks with their priorities
    for priority, task in tasks:
        priority_queue.insert((priority, task))

    # Process tasks in order of priority
    print("\nProcessing tasks by priority:")
    while len(priority_queue) > 0:
        priority, task = priority_queue.extract_max()
        print(f"Processing: {task} (Priority: {priority})")
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


