# Knapsack Problem implementation using Dynamic Programming
# The knapsack problem is a problem in combinatorial optimization where we need to
# maximize the value of items in a knapsack without exceeding the weight capacity

def knapsack_01(weights, values, capacity):
    """
    Solves the 0/1 Knapsack Problem using Dynamic Programming.

    This function finds the maximum value that can be obtained by selecting a subset of items
    where each item can be chosen only once (0 or 1 times), such that the total weight
    does not exceed the knapsack capacity.

    Args:
        weights (List[int]): List of weights for each item
        values (List[int]): List of values for each item
        capacity (int): Maximum weight capacity of the knapsack

    Returns:
        int: Maximum value that can be obtained

    Example:
        >>> weights = [2, 3, 4, 5]
        >>> values = [3, 4, 5, 6]
        >>> capacity = 8
        >>> knapsack_01(weights, values, capacity)
        10  # Best combination: items 0 and 2 (weights 2+4=6, values 3+5=8)
    """
    n = len(weights)  # Number of items

    # Initialize DP table (n+1 rows, capacity+1 columns)
    # dp[i][w] represents the maximum value that can be obtained using the first i items
    # and with a maximum weight of w
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    # Fill the DP table bottom-up
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # If current item's weight is less than or equal to the capacity w,
            # we have two choices: take it or leave it
            if weights[i-1] <= w:
                # Maximum of: (value of current item + value of remaining capacity after taking the item)
                # or (value without taking current item)
                dp[i][w] = max(values[i-1] + dp[i-1][w-weights[i-1]], dp[i-1][w])
            else:
                # If current item's weight exceeds capacity, we can't take it
                dp[i][w] = dp[i-1][w]

    return dp[n][capacity]


def knapsack_01_with_items(weights, values, capacity):
    """
    Solves the 0/1 Knapsack Problem using Dynamic Programming and returns the selected items.

    Args:
        weights (List[int]): List of weights for each item
        values (List[int]): List of values for each item
        capacity (int): Maximum weight capacity of the knapsack

    Returns:
        tuple: (maximum value, list of indices of selected items)

    Example:
        >>> weights = [2, 3, 4, 5]
        >>> values = [3, 4, 5, 6]
        >>> capacity = 8
        >>> knapsack_01_with_items(weights, values, capacity)
        (10, [0, 2])  # Max value 10 by selecting items at indices 0 and 2
    """
    n = len(weights)  # Number of items

    # Initialize DP table
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    # Fill the DP table bottom-up
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(values[i-1] + dp[i-1][w-weights[i-1]], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]

    # Backtrack to find the selected items
    max_value = dp[n][capacity]
    selected_items = []
    w = capacity

    for i in range(n, 0, -1):
        # If the value comes from including the current item
        if dp[i][w] != dp[i-1][w]:
            selected_items.append(i-1)  # Add the item index
            w -= weights[i-1]  # Reduce the remaining capacity

    # Reverse to get items in original order
    selected_items.reverse()

    return max_value, selected_items


# Example usage
if __name__ == "__main__":
    # Example 1: Basic knapsack
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 6]
    capacity = 8

    max_value = knapsack_01(weights, values, capacity)
    print(f"Maximum value: {max_value}")

    # Example 2: With item selection
    max_value, selected_items = knapsack_01_with_items(weights, values, capacity)
    print(f"Maximum value: {max_value}")
    print(f"Selected items (indices): {selected_items}")

    # Display the selected items with their weights and values
    total_weight = sum(weights[i] for i in selected_items)
    print("\nSelected items:")
    for i in selected_items:
        print(f"Item {i}: Weight = {weights[i]}, Value = {values[i]}")
    print(f"Total weight: {total_weight}")
    print(f"Total value: {max_value}")
