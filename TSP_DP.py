    # Traveling Salesman Problem (TSP) implementation using Dynamic Programming
    # The TSP finds the shortest possible route that visits every city exactly once and returns to the origin

    def tsp(cost, return_path=False):
    """
    Solves the Traveling Salesman Problem (TSP) using Dynamic Programming (Held-Karp algorithm).

    This function finds the minimum cost path that visits all cities exactly once and returns
    to the starting city. It uses a bitmask DP approach with time complexity O(n^2 * 2^n).

    Args:
        cost (List[List[int]]): A n×n matrix where cost[i][j] represents the cost of traveling
                               from city i to city j. Must be a square matrix.
        return_path (bool): If True, returns both the minimum cost and the optimal path.
                          If False, returns only the minimum cost.

    Returns:
        float or tuple: If return_path is False, returns the minimum cost of the TSP tour.
                       If return_path is True, returns (min_cost, path) where path is a list
                       of cities in the optimal tour order.

    Example:
        >>> cost = [
        ...     [0, 10, 15, 20],
        ...     [10, 0, 35, 25],
        ...     [15, 35, 0, 30],
        ...     [20, 25, 30, 0]
        ... ]
        >>> tsp(cost)
        80  # Represents optimal tour: 0 → 1 → 3 → 2 → 0
        >>> tsp(cost, return_path=True)
        (80, [0, 1, 3, 2, 0])  # Cost and the optimal path
    """
    # Get number of cities
    n = len(cost)
    # Initialize DP table: dp[mask][last] = min cost to visit cities in mask ending at 'last'
    dp = [[float('inf')] * n for _ in range(1 << n)]
    # If we need to track the path, store the predecessor for each state
    if return_path:
        parent = [[None] * n for _ in range(1 << n)]
    # Base case: Start at node 0 with cost 0
    dp[1 << 0][0] = 0  # Start at node 0

    # Iterate through all possible subsets of cities (represented as bitmasks)
    for mask in range(1 << n):
        # Iterate through all possible last cities in current subset
        for u in range(n):
            # Skip if city u is not in the current subset
            if not (mask & (1 << u)):
                continue
            # Try to extend path by visiting a new city v
            for v in range(n):
                # Consider only cities not yet visited
                if not (mask & (1 << v)):
                    # Create new mask that includes city v
                    new_mask = mask | (1 << v)
                    # Update dp table if a better path is found
                    new_cost = dp[mask][u] + cost[u][v]
                    if new_cost < dp[new_mask][v]:
                        dp[new_mask][v] = new_cost
                        if return_path:
                            parent[new_mask][v] = u

    # Find the final city that yields minimum cost when returning to start
    final_mask = (1 << n) - 1  # All cities visited
    min_cost = float('inf')
    last_city = None

    for u in range(n):
        if dp[final_mask][u] + cost[u][0] < min_cost:
            min_cost = dp[final_mask][u] + cost[u][0]
            last_city = u

    # If we don't need the path, just return the minimum cost
    if not return_path:
        return min_cost

    # Reconstruct the optimal path
    path = [0]  # Start with the ending city (0)
    path.insert(0, last_city)  # Add the last city before returning to 0

    current_mask = final_mask
    current_city = last_city

    # Work backwards to reconstruct the path
    while current_mask != (1 << 0):
        prev_city = parent[current_mask][current_city]
        path.insert(0, prev_city)
        current_mask = current_mask & ~(1 << current_city)  # Remove current city from mask
        current_city = prev_city

    return min_cost, path

# Example: Cost matrix for 4 cities (0, 1, 2, 3)
# Each entry cost[i][j] represents the cost to travel from city i to city j
# Diagonal elements are 0 as the cost to stay in the same city is 0
cost = [
    [0, 10, 15, 20],  # Costs from city 0 to cities 0,1,2,3
    [10, 0, 35, 25],   # Costs from city 1 to cities 0,1,2,3
    [15, 35, 0, 30],   # Costs from city 2 to cities 0,1,2,3
    [20, 25, 30, 0]    # Costs from city 3 to cities 0,1,2,3
]

# Calculate and print the minimum cost of the TSP tour
min_cost = tsp(cost)
print(f"Minimum cost: {min_cost}")  # Output: 80

# Calculate and print both the minimum cost and the optimal path
min_cost, path = tsp(cost, return_path=True)
print(f"Minimum cost: {min_cost}")
print(f"Optimal path: {path}")  # Shows the sequence of cities to visit

# Format the path for nice display
path_str = " → ".join(str(city) for city in path)
print(f"Tour: {path_str}")