from collections import deque
from typing import List, Optional

def topological_sort(num_nodes: int, edges: List[List[int]]) -> Optional[List[int]]:
    """
    Return a topological ordering of the nodes 0..num_nodes-1 if one exists,
    otherwise return None.

    Parameters
    ----------
    num_nodes : int
        Number of nodes in the graph.
    edges : List[List[int]]
        List of directed edges [u, v] meaning u must come before v.

    Returns
    -------
    Optional[List[int]]
        A list of nodes in topological order, or None if the graph contains a cycle.
    """
    # Build adjacency list and indegree array
    adj = [[] for _ in range(num_nodes)]
    indegree = [0] * num_nodes

    for u, v in edges:
        # Optional index validation
        if not (0 <= u < num_nodes and 0 <= v < num_nodes):
            raise ValueError(f"Edge ({u}, {v}) contains out-of-range node.")
        adj[u].append(v)
        indegree[v] += 1

    # Initialize queue with nodes having indegree 0
    queue = deque([i for i, d in enumerate(indegree) if d == 0])
    result = []

    while queue:
        u = queue.popleft()
        result.append(u)
        for v in adj[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)

    # If all nodes are processed, return the ordering; otherwise a cycle exists
    return result if len(result) == num_nodes else None