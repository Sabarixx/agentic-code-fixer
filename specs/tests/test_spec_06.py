from specs.reference.spec_06 import search


def test_search_found_in_right_half():
    assert search([4, 5, 6, 7, 0, 1, 2], 0) == 4


def test_search_missing():
    assert search([4, 5, 6, 7, 0, 1, 2], 3) == -1


def test_search_single_hit():
    assert search([1], 1) == 0


def test_search_unrotated():
    assert search([1, 2, 3, 4, 5], 4) == 3


def test_search_pivot_at_one():
    assert search([3, 1], 1) == 1
