#!/usr/bin/env python3

"""
Implementation of the 0/1 Knapsack Problem using Dynamic Programming.

The 0/1 Knapsack Problem involves selecting items with different weights and values
to maximize total value while keeping the total weight under a given capacity.
Each item can only be selected once (0/1 property).
"""

import numpy as np
import matplotlib.pyplot as plt
import time
import random


def knapsack_dp(values, weights, capacity, return_items=False):
    """
    Solve the 0/1 knapsack problem using dynamic programming.

    Args:
        values: List of values for each item
        weights: List of weights for each item
        capacity: Maximum weight capacity of the knapsack
        return_items: If True, returns selected items; if False, returns only max value

    Returns:
        int or tuple: Maximum value, or (maximum value, selected items) if return_items=True

    Example:
        >>> weights = [2, 3, 4, 5]
        >>> values = [3, 4, 5, 6]
        >>> capacity = 8
        >>> knapsack_dp(values, weights, capacity)
        10
        >>> knapsack_dp(values, weights, capacity, return_items=True)
        (10, [1, 3])  # Best combination: items 1 and 3 (weights 3+5=8, values 4+6=10)
    """
    n = len(values)

    # Initialize DP table with zeros
    # dp[i][w] represents the maximum value that can be obtained using first i items
    # and with a maximum weight capacity of w
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    # Build the DP table
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # If current item is too heavy, skip it
            if weights[i - 1] > w:
                dp[i][w] = dp[i - 1][w]
            else:
                # Max of (excluding current item, including current item)
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - weights[i - 1]] + values[i - 1])

    max_value = dp[n][capacity]

    if not return_items:
        return max_value

    # Reconstruct the solution (which items are selected)
    selected_items = []
    w = capacity
    for i in range(n, 0, -1):
        # If item i is included
        if dp[i][w] != dp[i - 1][w]:
            selected_items.append(i - 1)
            w -= weights[i - 1]

    # Reverse to get items in original order
    selected_items.reverse()

    return max_value, selected_items


def knapsack_recursive(values, weights, capacity, n=None, memo=None):
    """
    Solve the 0/1 knapsack problem using recursive approach with memoization.

    Args:
        values: List of values for each item
        weights: List of weights for each item
        capacity: Maximum weight capacity of the knapsack
        n: Number of items to consider (defaults to len(values))
        memo: Memoization dictionary

    Returns:
        Maximum value that can be obtained
    """
    if n is None:
        n = len(values)

    # Initialize memoization dictionary
    if memo is None:
        memo = {}

    # Base case: no items or no capacity
    if n == 0 or capacity == 0:
        return 0

    # Check if result is already memoized
    if (n, capacity) in memo:
        return memo[(n, capacity)]

    # If weight of nth item is more than capacity, skip it
    if weights[n - 1] > capacity:
        result = knapsack_recursive(values, weights, capacity, n - 1, memo)
    else:
        # Return max of two cases:
        # 1. nth item is included
        # 2. nth item is not included
        include = values[n - 1] + knapsack_recursive(values, weights, capacity - weights[n - 1], n - 1, memo)
        exclude = knapsack_recursive(values, weights, capacity, n - 1, memo)
        result = max(include, exclude)

    # Memoize the result
    memo[(n, capacity)] = result
    return result


def visualize_knapsack_solution(values, weights, capacity, selected):
    """
    Visualize the knapsack problem solution.

    Args:
        values: List of values for each item
        weights: List of weights for each item
        capacity: Maximum weight capacity
        selected: List of selected item indices
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Plot all items as circles with sizes proportional to weights
    # and colors based on values
    all_x = np.random.rand(len(weights))
    all_y = np.random.rand(len(weights))

    # Normalize for visualization
    sizes = [50 + 500 * (w / max(weights)) for w in weights]
    colors = [plt.cm.viridis(v / max(values)) for v in values]

    # Plot all items
    ax1.scatter(all_x, all_y, s=sizes, c=colors, alpha=0.6)

    # Add item labels
    for i, (x, y) in enumerate(zip(all_x, all_y)):
        ax1.annotate(f"{i}\n(w={weights[i]}, v={values[i]})",
                     (x, y), ha='center', va='center', fontsize=8)

    ax1.set_title("All Available Items")
    ax1.set_xlabel("X (arbitrary position)")
    ax1.set_ylabel("Y (arbitrary position)")
    ax1.set_xlim(-0.1, 1.1)
    ax1.set_ylim(-0.1, 1.1)
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Plot selected items and knapsack
    selected_x = [all_x[i] for i in selected]
    selected_y = [all_y[i] for i in selected]
    selected_sizes = [sizes[i] for i in selected]
    selected_colors = [colors[i] for i in selected]

    # Draw knapsack as a rectangle
    knapsack = plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=False, edgecolor='black',
                             linestyle='--', linewidth=2)
    ax2.add_patch(knapsack)

    # Plot selected items
    ax2.scatter(selected_x, selected_y, s=selected_sizes, c=selected_colors, alpha=0.8)

    # Add item labels for selected items
    for i, idx in enumerate(selected):
        ax2.annotate(f"{idx}\n(w={weights[idx]}, v={values[idx]})",
                     (selected_x[i], selected_y[i]), ha='center', va='center', fontsize=8)

    # Add summary
    total_weight = sum(weights[i] for i in selected)
    total_value = sum(values[i] for i in selected)
    ax2.set_title(f"Selected Items - Total Value: {total_value}, Total Weight: {total_weight}/{capacity}")
    ax2.set_xlabel("X (arbitrary position)")
    ax2.set_ylabel("Y (arbitrary position)")
    ax2.set_xlim(-0.1, 1.1)
    ax2.set_ylim(-0.1, 1.1)
    ax2.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig('knapsack_solution.png')
    plt.show()


def generate_random_items(n, max_weight=100, max_value=100, seed=None):
    """
    Generate random items for the knapsack problem.

    Args:
        n: Number of items to generate
        max_weight: Maximum possible weight for an item
        max_value: Maximum possible value for an item
        seed: Random seed for reproducibility

    Returns:
        Tuple of (values, weights)
    """
    if seed is not None:
        random.seed(seed)

    weights = [random.randint(1, max_weight) for _ in range(n)]
    values = [random.randint(1, max_value) for _ in range(n)]

    return values, weights


def compare_algorithms(values, weights, capacity):
    """
    Compare different knapsack algorithms and their performance.

    Args:
        values: List of values for each item
        weights: List of weights for each item
        capacity: Maximum weight capacity

    Returns:
        Dict with algorithm results and timing information
    """
    results = {}

    # Test dynamic programming approach
    start_time = time.time()
    dp_value, dp_items = knapsack_dp(values, weights, capacity, return_items=True)
    dp_time = time.time() - start_time

    results['dp'] = {
        'value': dp_value,
        'items': dp_items,
        'time': dp_time
    }

    # Test recursive approach
    start_time = time.time()
    recursive_value = knapsack_recursive(values, weights, capacity)
    recursive_time = time.time() - start_time

    results['recursive'] = {
        'value': recursive_value,
        'time': recursive_time
    }

    return results


def main():
    """Main function demonstrating knapsack problem solutions."""
    print("=== Knapsack Problem Demo ===\n")

    # Example 1: Basic problem
    print("Example 1: Basic Knapsack Problem")
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 6]
    capacity = 8

    print(f"Items: {list(zip(weights, values))}")
    print(f"Capacity: {capacity}")

    max_value, selected_items = knapsack_dp(values, weights, capacity, return_items=True)
    total_weight = sum(weights[i] for i in selected_items)

    print(f"Maximum value: {max_value}")
    print(f"Selected items (indices): {selected_items}")
    print(f"Selected items details:")
    for i in selected_items:
        print(f"  Item {i}: Weight = {weights[i]}, Value = {values[i]}")
    print(f"Total weight: {total_weight}/{capacity}")
    print()

    # Example 2: Random larger problem
    print("Example 2: Larger Random Problem")
    n_items = 15
    knapsack_capacity = 100

    values, weights = generate_random_items(n_items, seed=42)

    print(f"Number of items: {n_items}")
    print(f"Capacity: {knapsack_capacity}")

    results = compare_algorithms(values, weights, knapsack_capacity)

    print(f"\nResults:")
    print(f"DP Algorithm: Value = {results['dp']['value']}, Time = {results['dp']['time']:.6f}s")
    print(f"Recursive Algorithm: Value = {results['recursive']['value']}, Time = {results['recursive']['time']:.6f}s")
    print(f"Selected items: {results['dp']['items']}")

    # Visualize the solution
    print("\nGenerating visualization...")
    visualize_knapsack_solution(values, weights, knapsack_capacity, results['dp']['items'])


# Example usage and testing
if __name__ == "__main__":
    main()