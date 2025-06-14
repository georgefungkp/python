#!/usr/bin/env python3

"""
Implementation of Dijkstra's Shortest Path Algorithm.

This algorithm finds the shortest path from a source vertex to all other vertices
in a weighted graph. This implementation works with both directed and undirected graphs.
"""

import matplotlib.pyplot as plt
import numpy as np
from math import inf
import heapq


class Graph:
    def __init__(self, vertices):
        """
        Initialize a graph with a given number of vertices.

        Args:
            vertices: Number of vertices in the graph
        """
        self.V = vertices
        self.graph = [[] for _ in range(vertices)]
        self.pos = {}  # For visualization - positions of vertices

    def add_edge(self, u, v, w):
        """
        Add an edge from vertex u to vertex v with weight w.

        Args:
            u: Source vertex
            v: Destination vertex
            w: Weight of the edge
        """
        self.graph[u].append((v, w))

    def add_undirected_edge(self, u, v, w):
        """
        Add an undirected edge between vertices u and v with weight w.

        Args:
            u: First vertex
            v: Second vertex
            w: Weight of the edge
        """
        self.add_edge(u, v, w)
        self.add_edge(v, u, w)  # Add edge in both directions

    def set_position(self, vertex, pos):
        """
        Set the position of a vertex for visualization.

        Args:
            vertex: Vertex index
            pos: Tuple (x, y) with position coordinates
        """
        self.pos[vertex] = pos

    def dijkstra(self, src):
        """
        Find the shortest paths from source vertex to all other vertices.

        Args:
            src: Source vertex

        Returns:
            Tuple of (distances, predecessors) where:
            - distances[i] is the shortest distance from src to i
            - predecessors[i] is the predecessor of i in the shortest path
        """
        # Initialize distances with infinity and src with 0
        dist = [inf] * self.V
        dist[src] = 0

        # Initialize predecessors with -1
        pred = [-1] * self.V

        # Priority queue for vertices to process
        # Format: (distance, vertex)
        pq = [(0, src)]

        # Set to track processed vertices
        processed = set()

        while pq:
            # Get vertex with minimum distance
            current_dist, u = heapq.heappop(pq)

            # Skip if already processed or found a better path
            if u in processed or current_dist > dist[u]:
                continue

            # Mark as processed
            processed.add(u)

            # Check all adjacent vertices
            for v, weight in self.graph[u]:
                # Relaxation step
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    pred[v] = u
                    heapq.heappush(pq, (dist[v], v))

        return dist, pred

    def get_path(self, src, dest, predecessors):
        """
        Reconstruct the path from source to destination using predecessors.

        Args:
            src: Source vertex
            dest: Destination vertex
            predecessors: List of predecessors from dijkstra()

        Returns:
            List representing the path from src to dest, or empty list if no path exists
        """
        if dest == src:
            return [src]

        if predecessors[dest] == -1:
            return []  # No path exists

        path = []
        current = dest

        # Traverse from destination to source using predecessors
        while current != -1:
            path.append(current)
            current = predecessors[current]

        # Reverse to get path from source to destination
        return path[::-1]

    def visualize(self, distances=None, path=None, src=None):
        """
        Visualize the graph with optional highlighting of distances and path.

        Args:
            distances: Optional list of distances from source to each vertex
            path: Optional list representing a path to highlight
            src: Optional source vertex to highlight
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 8))

        # Generate positions if not provided
        if not self.pos:
            # Place vertices in a circle
            for i in range(self.V):
                angle = 2 * np.pi * i / self.V
                self.pos[i] = (np.cos(angle), np.sin(angle))

        # Draw edges
        edge_colors = []
        for u in range(self.V):
            for v, w in self.graph[u]:
                # Check if edge is in the path
                in_path = False
                if path and len(path) > 1:
                    for i in range(len(path) - 1):
                        if path[i] == u and path[i + 1] == v:
                            in_path = True

                color = 'red' if in_path else 'black'
                edge_colors.append(color)

                # Draw the edge
                ax.plot([self.pos[u][0], self.pos[v][0]],
                       [self.pos[u][1], self.pos[v][1]],
                       color=color, linewidth=2 if in_path else 1)

                # Draw the weight
                mid_x = (self.pos[u][0] + self.pos[v][0]) / 2
                mid_y = (self.pos[u][1] + self.pos[v][1]) / 2
                ax.text(mid_x, mid_y, str(w), fontsize=8, ha='center', va='center',
                       bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.2'))

        # Draw vertices
        for v in range(self.V):
            # Determine node color
            if src is not None and v == src:
                node_color = 'green'  # Source node
            elif path and v in path:
                node_color = 'red'    # Path node
            else:
                node_color = 'skyblue'

            # Draw the vertex
            circle = plt.Circle(self.pos[v], 0.1, color=node_color, zorder=10)
            ax.add_patch(circle)

            # Add vertex label
            ax.text(self.pos[v][0], self.pos[v][1], str(v), fontsize=10,
                   ha='center', va='center', color='white', fontweight='bold', zorder=11)

            # Add distance label if provided
            if distances:
                dist_text = str(distances[v]) if distances[v] != inf else '∞'
                offset_x = 0.15 * np.cos(np.pi/4)
                offset_y = 0.15 * np.sin(np.pi/4)
                ax.text(self.pos[v][0] + offset_x, self.pos[v][1] + offset_y, 
                       dist_text, fontsize=8, ha='center', va='center',
                       bbox=dict(facecolor='yellow', alpha=0.7, boxstyle='round,pad=0.1'))

        # Set axis properties
        ax.set_aspect('equal')
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.axis('off')

        # Set title
        if src is not None:
            plt.title(f"Dijkstra's Algorithm from Source {src}")
        else:
            plt.title("Graph Visualization")

        plt.savefig('dijkstra_graph.png')
        plt.show()


def create_example_graph():
    """
    Create an example graph for demonstration.

    Returns:
        Graph object with example data
    """
    # Create a graph with 6 vertices
    g = Graph(6)

    # Add edges
    g.add_undirected_edge(0, 1, 4)
    g.add_undirected_edge(0, 2, 2)
    g.add_undirected_edge(1, 2, 5)
    g.add_undirected_edge(1, 3, 10)
    g.add_undirected_edge(2, 3, 3)
    g.add_undirected_edge(2, 4, 8)
    g.add_undirected_edge(3, 4, 2)
    g.add_undirected_edge(3, 5, 7)
    g.add_undirected_edge(4, 5, 6)

    # Set positions for nice visualization
    g.set_position(0, (-1.0, 0.5))
    g.set_position(1, (-0.5, 1.0))
    g.set_position(2, (0.0, 0.0))
    g.set_position(3, (0.5, 1.0))
    g.set_position(4, (0.8, 0.0))
    g.set_position(5, (1.0, 0.5))

    return g


def main():
    # Create example graph
    g = create_example_graph()

    # Choose source vertex
    src = 0
    print(f"Finding shortest paths from vertex {src}...")

    # Run Dijkstra's algorithm
    distances, predecessors = g.dijkstra(src)

    # Print results
    print("\nShortest distances from source:")
    for i in range(g.V):
        print(f"Vertex {i}: {distances[i] if distances[i] != inf else 'Infinity'}")

    # Find path to a specific destination
    dest = 5
    path = g.get_path(src, dest, predecessors)

    if path:
        print(f"\nShortest path from {src} to {dest}: {' -> '.join(map(str, path))}")
        print(f"Path length: {distances[dest]}")
    else:
        print(f"\nNo path exists from {src} to {dest}")

    # Visualize the graph with the shortest path
    g.visualize(distances, path, src)


if __name__ == "__main__":
    main()
