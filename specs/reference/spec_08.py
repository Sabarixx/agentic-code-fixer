from collections import defaultdict, deque


def topological_sort(num_nodes: int, edges: list[list[int]]) -> list[int] | None:
    graph: dict[int, list[int]] = defaultdict(list)
    indegree = [0] * num_nodes
    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1
    queue = deque(i for i in range(num_nodes) if indegree[i] == 0)
    order: list[int] = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    if len(order) != num_nodes:
        return None
    return order


def is_valid_topo(num_nodes: int, edges: list[list[int]], order: list[int] | None) -> bool:
    if order is None:
        return False
    if sorted(order) != list(range(num_nodes)):
        return False
    position = {node: i for i, node in enumerate(order)}
    return all(position[u] < position[v] for u, v in edges)
