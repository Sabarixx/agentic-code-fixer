from specs.reference.spec_01 import two_sum


def test_two_sum_example_pair():
    assert sorted(two_sum([2, 7, 11, 15], 9)) == [0, 1]


def test_two_sum_not_adjacent():
    assert sorted(two_sum([3, 2, 4], 6)) == [1, 2]


def test_two_sum_duplicates():
    assert sorted(two_sum([3, 3], 6)) == [0, 1]


def test_two_sum_negatives():
    assert sorted(two_sum([-1, -2, -3, -4, -5], -8)) == [2, 4]


def test_two_sum_target_zero():
    assert sorted(two_sum([0, 4, 3, 0], 0)) == [0, 3]
