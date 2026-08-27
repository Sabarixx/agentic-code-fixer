from specs.reference.spec_04 import merge


def test_merge_overlapping_cluster():
    assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]


def test_merge_touching_endpoints():
    assert merge([[1, 4], [4, 5]]) == [[1, 5]]


def test_merge_contained_interval():
    assert merge([[1, 4], [2, 3]]) == [[1, 4]]


def test_merge_already_disjoint():
    assert merge([[1, 2], [3, 4], [5, 6]]) == [[1, 2], [3, 4], [5, 6]]


def test_merge_unsorted_input():
    assert merge([[8, 10], [1, 3], [2, 6]]) == [[1, 6], [8, 10]]
