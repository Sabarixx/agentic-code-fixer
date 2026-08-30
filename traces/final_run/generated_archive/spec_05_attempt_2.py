from collections import defaultdict
from typing import List

def group_anagrams(strs: List[str]) -> List[List[str]]:
    """
    Group strings that are anagrams of each other.

    Parameters
    ----------
    strs : List[str]
        A list of lowercase English words.

    Returns
    -------
    List[List[str]]
        A list of groups, each containing words that are anagrams.
        The relative order of groups and of words within a group is unspecified.
    """
    anagram_groups: defaultdict[str, List[str]] = defaultdict(list)

    for word in strs:
        # Use a tuple of sorted characters as the hashable key
        key = tuple(sorted(word))
        anagram_groups[key].append(word)

    return list(anagram_groups.values())