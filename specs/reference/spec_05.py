from collections import defaultdict


def group_anagrams(strs: list[str]) -> list[list[str]]:
    buckets: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for word in strs:
        buckets[tuple(sorted(word))].append(word)
    return list(buckets.values())
