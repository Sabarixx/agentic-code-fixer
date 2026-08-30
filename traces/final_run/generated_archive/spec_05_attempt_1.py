from collections import defaultdict
from typing import List

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
        A list of groups, each containing strings that are anagrams.
        The order of groups and the order within each group are not specified.
    """
    anagram_map = defaultdict(list)

    for s in strs:
        key = ''.join(sorted(s))
        anagram_map[key].append(s)

    return list(anagram_map.values())