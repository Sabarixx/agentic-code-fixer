from specs.reference.spec_05 import group_anagrams


def _normalize(groups: list[list[str]]) -> set[tuple[str, ...]]:
    return {tuple(sorted(group)) for group in groups}


def test_group_anagrams_classic():
    got = _normalize(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
    expected = _normalize([["eat", "tea", "ate"], ["tan", "nat"], ["bat"]])
    assert got == expected


def test_group_anagrams_singletons():
    got = _normalize(group_anagrams(["abc", "def"]))
    expected = _normalize([["abc"], ["def"]])
    assert got == expected


def test_group_anagrams_empty_string():
    got = _normalize(group_anagrams(["", ""]))
    expected = _normalize([["", ""]])
    assert got == expected


def test_group_anagrams_same_letters_different_count():
    got = _normalize(group_anagrams(["a", "aa", "aaa"]))
    expected = _normalize([["a"], ["aa"], ["aaa"]])
    assert got == expected


def test_group_anagrams_single_word():
    assert _normalize(group_anagrams(["xyz"])) == _normalize([["xyz"]])
