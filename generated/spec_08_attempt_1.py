from collections import deque
from typing import List, Optional

def topological_sort(num_nodes: int, edges: List[List[int]]) -> List[int] | None:
    """
    Perform a topological sort on a directed graph.

    Parameters
    ----------
    num_nodes : int
        Number of nodes in the graph, labeled from 0 to num_nodes-1.
    edges : List[List[int]]
        List of directed edges [u, v] meaning u must come before v.

    Returns
    -------
    List[int] | None
        A list representing a valid topological order of the nodes if one exists;
        otherwise, None if the graph contains a cycle.
    """
    # Build adjacency list and indegree array
    adj = [[] for _ in range(num_nodes)]
    indegree = [0] * num_nodes
    for u, v in edges:
        adj[u].append(v)
        indegree[v] += 1

    # Initialize queue with nodes having indegree 0
    q = deque([i for i, deg in enumerate(indegree) if deg == 0])
    order = []

    while q:
        node = q.popleft()
        order.append(node)
        for neigh in adj[node]:
            indegree[neigh] -= 1
            if indegree[neigh] == 0:
                q.append(neigh)

    # If all nodes are processed, return the order; otherwise, a cycle exists
    return order if len(order) == num_nodes else None