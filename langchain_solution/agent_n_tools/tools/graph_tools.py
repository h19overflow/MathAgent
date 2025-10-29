"""
Graph Theory Tools
Purpose: Analyze graphs and find shortest paths in networks.
Role: Extracts graph properties and solves pathfinding problems.
Dependencies: None (implements Dijkstra's algorithm)
"""

from langchain.tools import tool
from typing import List, Dict
import heapq


@tool
def analyze_graph_properties(vertices_json: str, edges_json: str) -> str:
    """
    Analyzes basic properties of a graph.

    Returns vertex set, edge set, number of vertices/edges, and sum of degrees.

    Args:
        vertices_json: JSON string list of vertex names (e.g., '["1", "2", "3", "4"]')
        edges_json: JSON string list of edge objects with 'from', 'to', and 'label'.
                   Format: '[{"from": "1", "to": "2", "label": "e1"}, ...]'

    Returns:
        String with JSON-formatted graph properties

    Example:
        analyze_graph_properties('["A","B","C"]', '[{"from":"A","to":"B","label":"e1"}]')
    """
    try:
        import json

        vertices = json.loads(vertices_json)
        edges = json.loads(edges_json)

        # Calculate degree of each vertex
        degree = {v: 0 for v in vertices}

        for edge in edges:
            degree[edge['from']] = degree.get(edge['from'], 0) + 1
            degree[edge['to']] = degree.get(edge['to'], 0) + 1

        sum_of_degrees = sum(degree.values())

        edge_labels = [edge['label'] for edge in edges]

        result = {
            "V": vertices,
            "n(V)": len(vertices),
            "E": edge_labels,
            "n(E)": len(edges),
            "sum_of_degrees": sum_of_degrees,
            "degrees": degree
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error analyzing graph: {str(e)}"


@tool
def find_shortest_path(edges_json: str, start_vertex: str, end_vertex: str,
                       optimize_for: str = "cost") -> str:
    """
    Finds the shortest path in a weighted directed graph using Dijkstra's algorithm.

    Args:
        edges_json: JSON string list of edges with weights.
                   Format: '[{"from": "P", "to": "Q", "weights": {"cost": 50, "time": 1}}, ...]'
        start_vertex: Starting vertex name
        end_vertex: Destination vertex name
        optimize_for: Weight type to optimize ("cost", "time", etc.)

    Returns:
        String with JSON-formatted path and total weight

    Example:
        find_shortest_path('[{"from":"A","to":"B","weights":{"cost":10}}]', 'A', 'B', 'cost')
    """
    try:
        import json

        edges = json.loads(edges_json)

        # Build adjacency list
        graph = {}
        for edge in edges:
            from_v = edge['from']
            to_v = edge['to']
            weight = edge['weights'].get(optimize_for, float('inf'))

            if from_v not in graph:
                graph[from_v] = []
            graph[from_v].append((to_v, weight))

        # Dijkstra's algorithm
        distances = {start_vertex: 0}
        previous = {}
        pq = [(0, start_vertex)]

        while pq:
            current_dist, current = heapq.heappop(pq)

            if current == end_vertex:
                break

            if current_dist > distances.get(current, float('inf')):
                continue

            for neighbor, weight in graph.get(current, []):
                distance = current_dist + weight

                if distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))

        # Reconstruct path
        if end_vertex not in distances:
            return f"No path found from {start_vertex} to {end_vertex}"

        path = []
        current = end_vertex
        while current in previous:
            path.append(current)
            current = previous[current]
        path.append(start_vertex)
        path.reverse()

        result = {
            "path": path,
            "total_weight": distances[end_vertex],
            "weight_type": optimize_for
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error finding shortest path: {str(e)}"


@tool
def calculate_graph_degree(vertices_json: str, edges_json: str, vertex: str) -> str:
    """
    Calculates the degree of a specific vertex in a graph.

    Args:
        vertices_json: JSON string list of vertex names
        edges_json: JSON string list of edges
        vertex: The vertex to calculate degree for

    Returns:
        String with the degree of the vertex

    Example:
        calculate_graph_degree('["A","B","C"]', '[{"from":"A","to":"B"}]', 'A')
    """
    try:
        import json

        edges = json.loads(edges_json)

        degree_count = 0
        for edge in edges:
            if edge['from'] == vertex:
                degree_count += 1
            if edge['to'] == vertex:
                degree_count += 1

        return f"Degree of vertex '{vertex}': {degree_count}"

    except Exception as e:
        return f"Error calculating degree: {str(e)}"
