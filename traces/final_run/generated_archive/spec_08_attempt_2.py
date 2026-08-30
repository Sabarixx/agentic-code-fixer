from collections import deque
from typing import List, Optional

def topological_sort(num_nodes: int, edges: List[List[int]]) -> Optional[List[int]]:
    """
    Return a topological ordering of the nodes 0..num_nodes-1 if one exists,
    otherwise return ``None``.
    """
    # Build adjacency list and indegree counts
    adjacency: List[List[int]] = [[] for _ in range(num_nodes)]
    indegree: List[int] = [0] * num_nodes

    for u, v in edges:
        if not (0 <= u < num_nodes and 0 <= v < num_nodes):
            raise ValueError(f"Edge ({u}, {v}) contains out‑of‑range node.")
        adjacency[u].append(v)
        indegree[v] += 1

    # Queue of nodes with no incoming edges
    zero_indegree = deque(i for i, d in enumerate(indegree) if d == 0)
    order: List[int] = []

    while zero_indegree:
        node = zero_indegree.popleft()
        order.append(node)
        for neighbour in adjacency[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                zero_indegree.append(neighbour)

    # If all nodes were processed, a valid ordering exists
    return order if len(order) == num_nodes else None