from specs.reference.spec_03 import is_valid


def test_valid_simple_pair():
    assert is_valid("()") is True


def test_valid_mixed_types():
    assert is_valid("()[]{}") is True


def test_invalid_wrong_type():
    assert is_valid("(]") is False


def test_invalid_wrong_order():
    assert is_valid("([)]") is False


def test_valid_nested():
    assert is_valid("{[]}") is True
