from collections import defaultdict
import heapq
from typing import List


class DSU:
    """
    Disjoint Set Union (Union-Find) data structure.
    Efficiently manages a partition of a set into disjoint subsets. Supports two key operations:
    - find(x): Finds the representative item of the set containing x, with path compression.
    - union(x, y): Merges the sets containing x and y. Returns True if merged, False if already in the same set.
    """

    def __init__(self, n):
        """
        Initialize the DSU for n elements (1-indexed).
        Each element is initially in its own set.
        """
        self.parent = list(range(n + 1))

    def find(self, x):
        """
        Find the root representative of the set that contains x.
        Uses path compression to flatten the tree structure, 
        making future queries faster.
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        """
        Merge the sets containing x and y.
        Returns True if the sets were separate and have now been merged,
        or False if x and y were already connected.
        """
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        self.parent[py] = px
        return True

class Solution:
    def processQueries(self, n: int, connections: List[List[int]], queries: List[List[int]]) -> List[int]:
        dsu = DSU(n)
        online = [True] * (n + 1)

        for u, v in connections: dsu.union(u, v)

        component_heap = defaultdict(list)
        for station in range(1, n + 1):
            root = dsu.find(station)
            heapq.heappush(component_heap[root], station)

        result = []

        for typ, x in queries:
            if typ == 2:
                online[x] = False
            else:
                if online[x]:
                    result.append(x)
                else:
                    root = dsu.find(x)
                    heap = component_heap[root]
                    while heap and not online[heap[0]]:
                        heapq.heappop(heap)
                    result.append(heap[0] if heap else -1)

        return result


c = 5
connections = [[1,2],[2,3],[3,4],[4,5]]
queries = [[1,3],[2,2],[1,1],[1,2]]

print(Solution().processQueries(c, connections, queries))