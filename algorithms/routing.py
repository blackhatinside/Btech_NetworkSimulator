# network_simulator/algorithms/routing.py

from typing import Dict, List, Tuple, Optional
import networkx as nx
import numpy as np

class RoutingAlgorithms:
    """
    Implementation of common routing algorithms used in telecommunication networks.
    Each algorithm includes visualization steps and detailed path computation.
    """

    @staticmethod
    def dijkstra(graph: nx.Graph, source: str, target: str) -> Tuple[List[str], Dict, List[Tuple]]:
        """
        Implements Dijkstra's shortest path algorithm with step tracking.
        Used in OSPF (Open Shortest Path First) protocol.

        Returns:
            - path: List of nodes in shortest path
            - distances: Dictionary of distances from source
            - steps: List of algorithm steps for visualization
        """
        distances = {node: float('infinity') for node in graph.nodes()}
        distances[source] = 0
        previous = {node: None for node in graph.nodes()}
        unvisited = list(graph.nodes())
        steps = []

        while unvisited:
            # Find minimum distance node
            current = min(unvisited, key=lambda node: distances[node])
            steps.append(('visit', current, distances[current]))

            if current == target:
                break

            unvisited.remove(current)

            # Update distances to neighbors
            for neighbor in graph.neighbors(current):
                if neighbor in unvisited:
                    weight = graph[current][neighbor]['weight']
                    new_distance = distances[current] + weight

                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current
                        steps.append(('update', neighbor, new_distance))

        # Reconstruct path
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        return path, distances, steps

    @staticmethod
    def bellman_ford(graph: nx.Graph, source: str, target: str) -> Tuple[Optional[List[str]], Dict, List[Tuple]]:
        """
        Implements Bellman-Ford algorithm with negative edge detection.
        Used in RIP (Routing Information Protocol).

        Args:
            graph: NetworkX graph object
            source: Starting node
            target: Destination node

        Returns:
            - path: List of nodes in shortest path (or None if negative cycle)
            - distances: Dictionary of distances from source
            - steps: List of algorithm steps for visualization
        """
        # Initialize distances and predecessors
        distances = {node: float('infinity') for node in graph.nodes()}
        distances[source] = 0
        predecessors = {node: None for node in graph.nodes()}
        steps = []

        # Add initial step to show starting state
        steps.append(('visit', source, 0))

        # Main relaxation loop
        for i in range(len(graph.nodes()) - 1):
            # Track if any updates were made in this iteration
            updates_made = False

            # Convert edges to list of tuples for consistent ordering
            edges = list(graph.edges())

            # Process each edge
            for u, v in edges:
                # Process edge in both directions (since it's an undirected graph)
                for a, b in [(u, v), (v, u)]:
                    weight = graph[a][b]['weight']
                    if distances[a] != float('infinity') and distances[a] + weight < distances[b]:
                        distances[b] = distances[a] + weight
                        predecessors[b] = a
                        updates_made = True
                        steps.append(('update', b, distances[b], a))

            # If no updates were made, we can terminate early
            if not updates_made:
                break

        # Check for negative weight cycles
        for u, v in graph.edges():
            weight = graph[u][v]['weight']
            if distances[u] + weight < distances[v] or distances[v] + weight < distances[u]:
                steps.append(('negative_cycle', u, v))
                return None, distances, steps

        # Reconstruct path
        if distances[target] == float('infinity'):
            return None, distances, steps

        path = []
        current = target
        while current is not None:
            path.append(current)
            current = predecessors[current]
        path.reverse()

        # Verify path exists from source to target
        if path[0] != source or path[-1] != target:
            return None, distances, steps

        return path, distances, steps

    @staticmethod
    def floyd_warshall(graph: nx.Graph) -> Tuple[Dict[Tuple[str, str], float], List[Tuple]]:
        """
        Implements Floyd-Warshall algorithm for all-pairs shortest paths.
        Useful for network-wide path optimization.
        """
        nodes = list(graph.nodes())
        n = len(nodes)

        # Initialize distance matrix
        dist = {(u, v): float('infinity') for u in nodes for v in nodes}
        next_hop = {(u, v): None for u in nodes for v in nodes}
        steps = []

        # Set initial distances
        for u in nodes:
            dist[(u, u)] = 0
            for v in graph.neighbors(u):
                dist[(u, v)] = graph[u][v]['weight']
                next_hop[(u, v)] = v

        # Floyd-Warshall algorithm
        for k in nodes:
            for i in nodes:
                for j in nodes:
                    if dist[(i, k)] + dist[(k, j)] < dist[(i, j)]:
                        dist[(i, j)] = dist[(i, k)] + dist[(k, j)]
                        next_hop[(i, j)] = next_hop[(i, k)]
                        steps.append(('update', i, j, k, dist[(i, j)]))

        return dist, next_hop, steps

    @staticmethod
    def prim_mst(graph: nx.Graph) -> Tuple[nx.Graph, List[Tuple]]:
        """
        Implements Prim's algorithm for Minimum Spanning Tree.
        Used in network design for minimum cost connections.
        """
        mst = nx.Graph()
        if not graph.nodes():
            return mst, []

        start_node = list(graph.nodes())[0]
        visited = {start_node}
        edges = []
        steps = []

        # Add all edges from start node
        edges.extend((graph[start_node][v]['weight'], start_node, v)
                    for v in graph.neighbors(start_node))
        edges.sort()  # Sort edges by weight

        while edges and len(visited) < len(graph.nodes()):
            weight, u, v = edges.pop(0)
            if v not in visited:
                visited.add(v)
                mst.add_edge(u, v, weight=weight)
                steps.append(('add_edge', u, v, weight))

                # Add new edges
                for w in graph.neighbors(v):
                    if w not in visited:
                        edges.append((graph[v][w]['weight'], v, w))
                edges.sort()

        return mst, steps

    @staticmethod
    def kruskal_mst(graph: nx.Graph) -> Tuple[nx.Graph, List[Tuple]]:
        """
        Implements Kruskal's algorithm for Minimum Spanning Tree.
        Alternative approach for network optimization.
        """
        mst = nx.Graph()
        for node in graph.nodes():
            mst.add_node(node)

        # Sort edges by weight
        edges = [(graph[u][v]['weight'], u, v) for u, v in graph.edges()]
        edges.sort()

        # Initialize disjoint set for each node
        parent = {node: node for node in graph.nodes()}
        rank = {node: 0 for node in graph.nodes()}
        steps = []

        def find(node):
            if parent[node] != node:
                parent[node] = find(parent[node])
            return parent[node]

        def union(u, v):
            if rank[u] < rank[v]:
                parent[u] = v
            elif rank[u] > rank[v]:
                parent[v] = u
            else:
                parent[v] = u
                rank[u] += 1

        # Process edges in order of increasing weight
        for weight, u, v in edges:
            root_u = find(u)
            root_v = find(v)

            if root_u != root_v:
                union(root_u, root_v)
                mst.add_edge(u, v, weight=weight)
                steps.append(('add_edge', u, v, weight))

        return mst, steps