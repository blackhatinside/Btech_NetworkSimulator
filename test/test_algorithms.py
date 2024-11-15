# network_simulator/tests/test_algorithms.py

import networkx as nx
from algorithms.routing import RoutingAlgorithms
import pytest

def load_test_graph(filename):
    """Load test graph from file"""
    graph = nx.Graph()

    with open(filename, 'r') as f:
        # Read first line containing number of vertices and edges
        n, m = map(int, f.readline().split())

        # Read edges
        for _ in range(m):
            u, v, w = map(int, f.readline().split())
            graph.add_edge(str(u), str(v), weight=w)

    return graph

def test_algorithms():
    """Test all routing algorithms with the test graph"""
    # Load test graph
    graph = load_test_graph('test3.txt')

    # Test Dijkstra's Algorithm
    print("\nTesting Dijkstra's Algorithm:")
    source = '0'
    target = '9'
    path, distances, steps = RoutingAlgorithms.dijkstra(graph, source, target)
    print(f"Path from {source} to {target}: {path}")
    print(f"Distance: {distances[target]}")

    # Test Bellman-Ford Algorithm
    print("\nTesting Bellman-Ford Algorithm:")
    path, distances, steps = RoutingAlgorithms.bellman_ford(graph, source, target)
    print(f"Path from {source} to {target}: {path}")
    print(f"Distance: {distances[target]}")

    # Test Floyd-Warshall Algorithm
    print("\nTesting Floyd-Warshall Algorithm:")
    distances, next_hop, steps = RoutingAlgorithms.floyd_warshall(graph)
    print(f"Distance from {source} to {target}: {distances[(source, target)]}")

    # Test Prim's MST Algorithm
    print("\nTesting Prim's MST Algorithm:")
    mst, steps = RoutingAlgorithms.prim_mst(graph)
    total_weight = sum(mst[u][v]['weight'] for u, v in mst.edges())
    print(f"MST total weight: {total_weight}")
    print(f"MST edges: {list(mst.edges())}")

    # Test Kruskal's MST Algorithm
    print("\nTesting Kruskal's MST Algorithm:")
    mst, steps = RoutingAlgorithms.kruskal_mst(graph)
    total_weight = sum(mst[u][v]['weight'] for u, v in mst.edges())
    print(f"MST total weight: {total_weight}")
    print(f"MST edges: {list(mst.edges())}")

if __name__ == "__main__":
    test_algorithms()