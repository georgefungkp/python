# Banker's Algorithm
# Implementation of the Banker's Algorithm for deadlock avoidance
# The algorithm determines if a system state is safe by simulating resource allocation
# https://www.geeksforgeeks.org/bankers-algorithm-in-operating-system-2/

# Driver code:
if __name__ == "__main__":

    # P0, P1, P2, P3, P4 are the Process names here
    n = 5  # Number of processes
    m = 3  # Number of resources

    # Allocation Matrix - represents resources currently allocated to each process
    # Each row represents a process, each column represents a resource type
    alloc = [[0, 1, 0], [2, 0, 0],
             [3, 0, 2], [2, 1, 1], [0, 0, 2]]

    # MAX Matrix - represents maximum resources needed by each process
    # This matrix defines the maximum demand of each process for each resource type
    max = [[5, 5, 3], [3, 2, 2],
           [9, 0, 2], [5, 2, 2], [8, 3, 3]]

    avail = [3, 3, 2]  # Available Resources - represents resources available in the system

    # Finish array to track which processes have finished
    f = [0] * n
    # Array to store the safe sequence of processes
    ans = [0] * n
    # Index to track position in the answer array
    ind = 0
    # Initialize all processes as unfinished (0)
    for k in range(n):
        f[k] = 0

    # Calculate Need matrix = MAX - Allocation
    # This represents additional resources each process may still request
    need = [[0 for i in range(m)] for i in range(n)]
    for i in range(n):
        for j in range(m):
            need[i][j] = max[i][j] - alloc[i][j]
    # Temporary variable for iterations
    y = 0
    # Main algorithm loop - run for maximum n iterations (theoretically, should find solution in n steps if one exists)
    # Using 10 as a conservative upper bound
    for k in range(10):
        # Iterate through all processes
        for i in range(n):
            # Check if process is unfinished
            if (f[i] == 0):
                # Assume process can be executed
                flag = 0
                # Check if all needed resources are available
                for j in range(m):
                    if (need[i][j] > avail[j]):
                        # If any needed resource exceeds available, process cannot run now
                        flag = 1
                        break

                # If all resources are available for this process
                if (flag == 0):
                    # Add process to safe sequence
                    ans[ind] = i
                    ind += 1
                    # Release allocated resources back to available pool
                    for y in range(m):
                        avail[y] += alloc[i][y]
                    # Mark process as finished
                    f[i] = 1

    # Print the safe sequence result
    print("Following is the SAFE Sequence")

    # Print all processes in the safe sequence except the last one
    for i in range(n - 1):
        print(" P", ans[i], " ->", sep="", end="")
    # Print the last process in the sequence without an arrow
    print(" P", ans[n - 1], sep="")


