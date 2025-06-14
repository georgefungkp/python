# Algorithm Implementations in Python

This repository contains implementations of classic algorithms and data structures in Python. Each implementation includes detailed comments, visualizations, and examples of usage.

## Implemented Algorithms

### 1. Traveling Salesman Problem (TSP) - Dynamic Programming

**File:** `TSP_DP.py`

An implementation of the Traveling Salesman Problem using dynamic programming approach. The TSP involves finding the shortest possible route that visits each city exactly once and returns to the origin city.

**Features:**
- O(n²·2ⁿ) time complexity solution using bit manipulation
- Random test case generation
- Path visualization with matplotlib
- Performance measurement

**Usage:**
```bash
python TSP_DP.py [number_of_cities]
```

### 2. Max Heap

**File:** `max_heap.py`

An implementation of the Max Heap data structure, where the value of each node is greater than or equal to the values of its children.

**Features:**
- Standard heap operations: insert, extract_max, peek
- Heap visualization using matplotlib
- Heap sort implementation

**Usage:**
```bash
python max_heap.py
```

### 3. Dijkstra's Shortest Path Algorithm

**File:** `dijkstra.py`

An implementation of Dijkstra's algorithm for finding the shortest paths from a source vertex to all other vertices in a weighted graph.

**Features:**
- Works with both directed and undirected graphs
- Efficient implementation using priority queue
- Path reconstruction
- Graph visualization with shortest path highlighting

**Usage:**
```bash
python dijkstra.py
```

### 4. 0/1 Knapsack Problem

**File:** `knapsack.py`

An implementation of the 0/1 Knapsack Problem using dynamic programming. The problem involves selecting items with different weights and values to maximize total value while keeping the total weight under a given capacity.

**Features:**
- Bottom-up dynamic programming approach
- Recursive implementation with memoization for comparison
- Solution visualization
- Random problem generation

**Usage:**
```bash
python knapsack.py
```

### 5. Longest Common Subsequence (LCS)

**File:** `lcs.py`

An implementation of the Longest Common Subsequence algorithm using dynamic programming. LCS finds the longest subsequence common to two sequences.

**Features:**
- Dynamic programming solution
- Subsequence reconstruction
- Visualization of the DP table

**Usage:**
```bash
python lcs.py
```

## Requirements

The implementations use the following Python packages:
- numpy
- matplotlib
- pillow (for some visualizations)

You can install the required packages using:
```bash
pip install numpy matplotlib pillow
```

