from collections import deque
from distutils.command.install import value


def minMoves(classroom, energy):
    """
    :type classroom: List[str]
    :type energy: int
    :rtype: int
    """
    m, n = len(classroom), len(classroom[0])
    energy_max = energy
    start = None
    litters = []

    for i in range(m):
        for j in range(n):
            c = classroom[i][j]
            if c == 'S':
                start = (i, j)
            elif c == 'L':
                litters.append((i, j))

    k = len(litters)  # Count total number of litter pieces
    if k == 0:  # If no litter to collect, return 0 moves
        return 0

    # Create a mapping from litter positions to indices for bit manipulation
    litter_index = {pos: idx for idx, pos in enumerate(litters)}

    # Create a bit mask that represents all litter collected (all bits set to 1)
    full_mask = (1 << k) - 1

    # Initialize 3D DP array to track best energy levels at each state
    # Dimensions: [row][column][bitmask of collected litter]
    # Value: best (maximum) energy level achievable at this state
    best_e = [
        [ [-1] * (1<<k) for _ in range(n) ]
        for __ in range(m)
    ]

    # Extract starting position coordinates
    sx, sy = start
    init_mask = 0  # Initial bitmask: no litter collected yet

    # Set starting state with full energy
    best_e[sx][sy][init_mask] = energy_max

    # Initialize BFS queue with: (x, y, litter_mask, moves_so_far)
    dq = deque([ (sx, sy, init_mask, 0) ])

    # Define the four possible movement directions: down, up, right, left
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]

    # Begin BFS traversal
    while dq:
        # Dequeue current state
        x, y, mask, moves = dq.popleft()
        print('[{},{}] mask: {}, move: {}'.format(x,y,mask,moves))  # Debug output
        curr_e = best_e[x][y][mask]  # Current energy level

        # If all litter has been collected, return the number of moves
        if mask == full_mask:
            return moves

        # Try all four possible movement directions
        for dx, dy in dirs:
            new_x, new_y = x+dx, y+dy  # Calculate new position

            # Skip if new position is outside the grid boundaries
            if not (0 <= new_x < m and 0 <= new_y < n):
                continue

            cell = classroom[new_x][new_y]  # Get cell type at new position
            if cell == 'X':  # Skip obstacles
                continue

            # Calculate new energy level after move (costs 1 energy unit per move)
            new_energy = curr_e - 1
            if new_energy < 0:  # Skip if we don't have enough energy
                continue

            # Recharge if the new cell is a recharge station
            if cell == 'R':
                new_energy = energy_max

            # Update the litter collection mask if we find litter
            new_mask = mask
            if cell == 'L':
                # Set the bit corresponding to this litter position
                new_mask |= 1 << litter_index[(new_x, new_y)]

            # Skip if we already have a better (higher) energy level for this state
            if new_energy <= best_e[new_x][new_y][new_mask]:
                continue

            # Update best energy level for this state
            best_e[new_x][new_y][new_mask] = new_energy
            # Add new state to the queue
            dq.append((new_x, new_y, new_mask, moves+1))

    # If we've explored all reachable states and haven't collected all litter, it's impossible
    return -1

# Test cases for the minMoves function

# Test Case 1: Simple 2x2 grid (commented out)
# print(minMoves(["S.", "XL"], 2))

# Test Case 2: Another simple 2x2 grid (commented out)
# print(minMoves(["LS", "RL"], 4))

# Test Case 3: 2x3 grid with obstacles, litter, and recharge stations
print(minMoves(["L.S", "RXL"], 5))  # Starting energy: 5

# Test Case 4: 4x5 grid with multiple litter pieces, obstacles, and recharge stations
print(minMoves(classroom = [
    "S....",  # Row 0: Starting position in the top-left corner
    "LXL.L",  # Row 1: Litter, obstacle, litter, empty, litter
    "R...X",  # Row 2: Recharge station, empty cells, obstacle
    "..L.R"   # Row 3: Empty cells, litter, empty, recharge station
],
energy = 3))  # Starting energy: 3

# Test Case 5: 5x4 grid with obstacles, litter, and recharge stations
print(minMoves(classroom = [
    "S...",  # Row 0: Starting position in the top-left corner
    ".L.L",  # Row 1: Empty, litter, empty, litter
    "X..R",  # Row 2: Obstacle, empty cells, recharge station
    ".L..",  # Row 3: Empty, litter, empty cells
    "R..."   # Row 4: Recharge station, empty cells
],
energy = 5))  # Starting energy: 5

# Test Case 6: 5x4 grid with many obstacles and litter pieces in a challenging layout
print(minMoves(classroom = [
    "S..L",  # Row 0: Starting position, empty cells, litter
    "XX.L",  # Row 1: Two obstacles, empty, litter
    "R..L",  # Row 2: Recharge station, empty cells, litter
    ".X.L",  # Row 3: Empty, obstacle, empty, litter
    "R..."   # Row 4: Recharge station, empty cells
],
energy = 10))  # Starting energy: 10

