from specs.reference.spec_02 import from_list, reverse_list, to_list


def test_reverse_five_nodes():
    assert to_list(reverse_list(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]


def test_reverse_two_nodes():
    assert to_list(reverse_list(from_list([1, 2]))) == [2, 1]


def test_reverse_empty():
    assert reverse_list(None) is None


def test_reverse_single():
    assert to_list(reverse_list(from_list([42]))) == [42]


def test_reverse_with_negatives():
    assert to_list(reverse_list(from_list([-1, 0, 1]))) == [1, 0, -1]
