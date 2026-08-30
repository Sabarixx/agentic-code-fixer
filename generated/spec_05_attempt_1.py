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
        List of groups, each group containing strings that are anagrams.
        Order of groups and order within groups is not specified.
    """
    if not strs:
        return []

    # Map from character count tuple to list of strings
    groups: Dict[Tuple[int, ...], List[str]] = {}

    for s in strs:
        # Count occurrences of each letter
        count = [0] * 26
        for ch in s:
            count[ord(ch) - 97] += 1
        key = tuple(count)
        groups.setdefault(key, []).append(s)

    return list(groups.values())