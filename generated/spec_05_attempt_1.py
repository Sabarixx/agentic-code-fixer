from typing import List, Dict, Tuple

def group_anagrams(strs: List[str]) -> List[List[str]]:
    """
    Group strings that are anagrams of each other.

    Parameters
    ----------
    strs : List[str]
        List of lowercase English strings.

    Returns
    -------
    List[List[str]]
        List of groups, each containing strings that are anagrams.
        Order of groups and order within groups is not specified.
    """
    if not strs:
        return []

    anagram_map: Dict[Tuple[int, ...], List[str]] = {}
    for s in strs:
        # Count occurrences of each letter (a-z)
        count = [0] * 26
        for ch in s:
            count[ord(ch) - 97] += 1
        key = tuple(count)
        anagram_map.setdefault(key, []).append(s)

    return list(anagram_map.values())