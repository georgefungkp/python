"""
Graph Traversal Algorithms: Breadth-First Search (BFS) and Depth-First Search (DFS)

This module implements the two fundamental graph traversal algorithms:
- BFS: Explores nodes level by level, finding shortest paths in unweighted graphs
- DFS: Explores as far as possible along each branch before backtracking

Both algorithms are essential for graph analysis, pathfinding, and many other applications.
"""

from collections import deque


def bfs(graph, start):
    """
    Breadth-First Search (BFS) implementation using a queue.

    BFS explores nodes level by level, visiting all neighbors of a node before
    moving to the next level. It uses a FIFO (First-In-First-Out) queue structure.

    Time Complexity: O(V + E) where V is vertices and E is edges
    Space Complexity: O(V) for the visited set and queue

    Applications:
    - Finding shortest path in unweighted graphs
    - Level-order traversal of trees
    - Finding connected components
    - Web crawling algorithms

    Args:
        graph (dict): Adjacency list representation of the graph
                     Format: {node: [list_of_neighbors]}
        start: The starting node for traversal

    Returns:
        None: Prints nodes in BFS order
    """
    # FIFO - First In, First Out (queue behavior)
    visited = set()  # Keep track of visited nodes to avoid cycles
    queue = deque([start])  # Initialize queue with starting node
    visited.add(start)  # Mark starting node as visited

    # Continue until queue is empty
    while queue:
        # Remove and get the first node from queue (FIFO)
        node = queue.popleft()
        print(node, end=" ")  # Process current node (can be any operation)

        # Explore all neighbors of current node
        for neighbor in graph[node]:
            # Only visit unvisited neighbors to avoid infinite loops
            if neighbor not in visited:
                visited.add(neighbor)  # Mark neighbor as visited
                queue.append(neighbor)  # Add neighbor to queue for future processing


def dfs_iterative(graph, start):
    """
    Depth-First Search (DFS) iterative implementation using a stack.

    DFS explores as far as possible along each branch before backtracking.
    It uses a LIFO (Last-In-First-Out) stack structure.

    Time Complexity: O(V + E) where V is vertices and E is edges
    Space Complexity: O(V) for the visited set and stack

    Applications:
    - Detecting cycles in graphs
    - Topological sorting
    - Finding strongly connected components
    - Solving maze problems
    - Backtracking algorithms

    Args:
        graph (dict): Adjacency list representation of the graph
                     Format: {node: [list_of_neighbors]}
        start: The starting node for traversal

    Returns:
        None: Prints nodes in DFS order
    """
    # LIFO - Last In, First Out (stack behavior)
    visited = set()  # Keep track of visited nodes to avoid cycles
    stack = [start]  # Initialize stack with starting node

    # Continue until stack is empty
    while stack:
        # Remove and get the last node from stack (LIFO)
        node = stack.pop()

        # Check if node hasn't been visited yet
        if node not in visited:
            visited.add(node)  # Mark current node as visited
            print(node, end=" ")  # Process current node (can be any operation)

            # Push neighbors onto stack in reverse order
            # This ensures left-to-right traversal when popped
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)  # Add unvisited neighbors to stack


def dfs_recursive(graph, node, visited=None):
    """
    Depth-First Search (DFS) recursive implementation.

    This is the classic recursive approach to DFS that naturally uses the
    call stack for maintaining the traversal order.

    Time Complexity: O(V + E) where V is vertices and E is edges
    Space Complexity: O(V) for the visited set and call stack (recursion depth)

    Advantages over iterative:
    - More intuitive and easier to understand
    - Cleaner code for complex operations
    - Natural handling of tree-like structures

    Disadvantages:
    - Risk of stack overflow for deep graphs
    - Less control over memory usage

    Args:
        graph (dict): Adjacency list representation of the graph
                     Format: {node: [list_of_neighbors]}
        node: The current node being processed
        visited (set, optional): Set of visited nodes. Defaults to None.

    Returns:
        None: Prints nodes in DFS order
    """
    # Initialize visited set on first call
    if visited is None:
        visited = set()

    # Mark current node as visited
    visited.add(node)
    print(node, end=" ")  # Process current node (can be any operation)

    # Recursively visit all unvisited neighbors
    for neighbor in graph[node]:
        if neighbor not in visited:
            # Recursive call for depth-first exploration
            dfs_recursive(graph, neighbor, visited)


# Example usage and testing
if __name__ == "__main__":
    # Sample graph representation as adjacency list
    # Graph structure:
    #     A
    #    / \
    #   B   C
    #  /   / \
    # D   E   F
    sample_graph = {
        'A': ['B', 'C'],
        'B': ['A', 'D'],
        'C': ['A', 'E', 'F'],
        'D': ['B'],
        'E': ['C'],
        'F': ['C']
    }

    print("Sample Graph:", sample_graph)
    print("\nTraversal Results:")

    print("BFS from A: ", end="")
    bfs(sample_graph, 'A')
    print()  # New line

    print("DFS Iterative from A: ", end="")
    dfs_iterative(sample_graph, 'A')
    print()  # New line

    print("DFS Recursive from A: ", end="")
    dfs_recursive(sample_graph, 'A')
    print()  # New line

    # Example with a different starting node
    print("\nStarting from node 'C':")
    print("BFS from C: ", end="")
    bfs(sample_graph, 'C')
    print()

    print("DFS from C: ", end="")
    dfs_recursive(sample_graph, 'C')
    print()