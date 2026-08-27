from specs.reference.spec_08 import is_valid_topo, topological_sort


def test_topo_diamond():
    edges = [[0, 1], [0, 2], [1, 3], [2, 3]]
    order = topological_sort(4, edges)
    assert is_valid_topo(4, edges, order)


def test_topo_cycle_returns_none():
    assert topological_sort(2, [[0, 1], [1, 0]]) is None


def test_topo_linear_chain():
    edges = [[0, 1], [1, 2], [2, 3]]
    order = topological_sort(4, edges)
    assert order == [0, 1, 2, 3]


def test_topo_disconnected():
    order = topological_sort(3, [])
    assert is_valid_topo(3, [], order)


def test_topo_self_contained_two_components():
    edges = [[0, 1], [2, 3]]
    order = topological_sort(4, edges)
    assert is_valid_topo(4, edges, order)
