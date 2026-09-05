from collections import deque
from typing import List, Optional

def topological_sort(num_nodes: int, edges: List[List[int]]) -> Optional[List[int]]:
    """
    Return a topological ordering of the nodes 0..num_nodes-1 given directed edges.
    If the graph contains a cycle, return None.

    Parameters
    ----------
    num_nodes : int
        Number of nodes in the graph.
    edges : List[List[int]]
        List of directed edges [u, v] meaning u must come before v.

    Returns
    -------
    Optional[List[int]]
        A list of nodes in topological order, or None if a cycle exists.
    """
    # Build adjacency list and indegree count
    adj = [[] for _ in range(num_nodes)]
    indegree = [0] * num_nodes
    for u, v in edges:
        adj[u].append(v)
        indegree[v] += 1

    # Initialize queue with nodes having indegree 0
    queue = deque([i for i in range(num_nodes) if indegree[i] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in adj[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    # If all nodes are processed, return order; otherwise cycle detected
    return order if len(order) == num_nodes else None