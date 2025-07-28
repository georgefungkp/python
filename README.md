# Algorithm Implementations in Python

This repository contains implementations of classic algorithms and data structures in Python. Each implementation includes detailed comments, examples, and educational content to help understand fundamental computer science concepts.

## Data Structures

### 1. Max Heap
**File:** `max_heap.py`

A complete implementation of the Max Heap data structure where parent nodes are greater than or equal to their children.

**Features:**
- Standard heap operations: insert, extract_max, get_max
- Heap visualization capabilities
- Priority queue implementation using heaps
- Heap sort demonstration
- Educational examples with detailed comments

### 2. Disjoint Set Union (DSU)
**File:** `DSU.py`

Implementation of the Union-Find data structure with path compression and union by rank optimizations.

**Features:**
- Efficient union and find operations
- Path compression for optimal performance
- Union by rank heuristic
- Applications in graph connectivity problems

### 3. Monotonic Stack
**File:** `monotonic_stack.py`

Implementation and applications of monotonic stack data structure for solving various algorithmic problems.

**Features:**
- Stack maintaining monotonic property
- Solutions to common problems like next greater element
- Time-efficient approaches to array processing problems

## Graph Algorithms

### 1. Breadth-First Search (BFS) and Depth-First Search (DFS)
**File:** `BFS_DFS.py`

Comprehensive implementations of fundamental graph traversal algorithms.

**Features:**
- BFS using queue (FIFO) for level-order traversal
- DFS using both iterative (stack) and recursive approaches
- Detailed comments explaining time/space complexity
- Applications in pathfinding and graph analysis

### 2. Dijkstra's Shortest Path Algorithm
**File:** `dijkstra.py`

Implementation of Dijkstra's algorithm for finding shortest paths in weighted graphs.

**Features:**
- Priority queue-based implementation
- Handles both directed and undirected graphs
- Path reconstruction capabilities
- Graph visualization with shortest path highlighting

### 3. Cycle Detection
**File:** `unidirection_cycle_detection.py`

Algorithm for detecting cycles in directed graphs using DFS-based approaches.

**Features:**
- Efficient cycle detection in directed graphs
- Applications in dependency resolution and deadlock detection

## Dynamic Programming

### 1. 0/1 Knapsack Problem
**File:** `knapsack.py`

Classic dynamic programming solution to the 0/1 Knapsack optimization problem.

**Features:**
- Bottom-up dynamic programming approach
- Space-optimized versions
- Solution reconstruction
- Random test case generation

### 2. Longest Common Subsequence (LCS)
**File:** `lcs.py`

Dynamic programming solution for finding the longest common subsequence between two sequences.

**Features:**
- DP table construction and visualization
- Subsequence reconstruction
- Applications in text comparison and version control

### 3. Edit Distance
**File:** `edit_distance.py`

Implementation of the Wagner-Fischer algorithm for computing edit distance (Levenshtein distance).

**Features:**
- Dynamic programming solution
- String transformation operations
- Applications in spell checking and DNA sequence analysis

### 4. Maximum Subarray Sum
**Files:** `max_subarray_sum.py`, `maximum_subarray.py`

Multiple approaches to solving the maximum subarray problem.

**Features:**
- Kadane's algorithm implementation
- Brute force and optimized solutions
- Handling of edge cases

## String Algorithms

### 1. Smallest Non-Repeating Character
**File:** `smallest-non-repeating.py`

Algorithms for finding non-repeating characters and substrings.

**Features:**
- First non-repeating character finder
- Minimum length non-repeating subarray
- Optimized single-pass solutions
- Sliding window technique applications

### 2. Substring Operations
**File:** `substring.py`

Various string processing and substring manipulation algorithms.

**Features:**
- Pattern matching algorithms
- String processing utilities
- Efficient substring operations

## Mathematical Algorithms

### 1. Fibonacci Sequence
**File:** `fibonacci.py`

Multiple implementations of Fibonacci number generation.

**Features:**
- Recursive, iterative, and matrix-based approaches
- Performance comparisons
- Mathematical properties exploration

### 2. Prime Factorization
**File:** `get_factors.py`

Algorithm for finding prime factors of integers.

**Features:**
- Efficient factorization methods
- Prime number utilities
- Mathematical applications

## Sorting Algorithms

### 1. Sorting Implementations
**File:** `sorting.py`

Collection of classic sorting algorithms with educational focus.

**Features:**
- Multiple sorting algorithm implementations
- Performance comparisons
- Best, average, and worst-case analysis

## Search Algorithms

### 1. Binary Search Examples
**File:** `binary_search_examples.py`

Comprehensive examples of binary search applications.

**Features:**
- Classic binary search implementation
- Variations and edge cases
- Applications in different problem domains

## Advanced Algorithms

### 1. Sweep Line Algorithm
**File:** `sweep_line.py`

Implementation of the sweep line technique for geometric problems.

**Features:**
- Line segment intersection detection
- Event-driven algorithm design
- Computational geometry applications

### 2. Banker's Algorithm
**File:** `banker_algorithm.py`

Implementation of the Banker's algorithm for deadlock avoidance in operating systems.

**Features:**
- Resource allocation and deadlock prevention
- Safety algorithm implementation
- Operating systems concepts demonstration

## Utilities and Examples

### 1. CSV Processing
**File:** `csv_read.py`

Utilities for reading and processing CSV data files.

### 2. Test Files
**File:** `test.py`

Test cases and examples for various algorithms.

### 3. Sample Data
**File:** `data.csv`

Sample dataset for testing data processing algorithms.

## Requirements

The implementations use standard Python libraries and some additional packages:

```bash
pip install numpy matplotlib
```