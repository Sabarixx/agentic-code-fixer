from typing import List

Interval = List[int]


def merge(intervals: List[Interval]) -> List[Interval]:
    """
    Merge all overlapping or adjacent intervals.

    Parameters
    ----------
    intervals : List[Interval]
        A list of intervals represented as [start, end].

    Returns
    -------
    List[Interval]
        A list of merged, non‑overlapping intervals covering all points in the input.

    Notes
    -----
    * Intervals that touch at endpoints (e.g., [1, 4] and [4, 5]) are merged.
    * The original input list is not modified.
    * An empty input returns an empty list.
    """
    if not intervals:
        return []

    # Sort by start, then by end for stability.
    sorted_intervals = sorted(intervals, key=lambda iv: (iv[0], iv[1]))

    merged_intervals: List[Interval] = []
    for start, end in sorted_intervals:
        if not merged_intervals or start > merged_intervals[-1][1]:
            merged_intervals.append([start, end])
        else:
            # Extend the last interval if needed.
            merged_intervals[-1][1] = max(merged_intervals[-1][1], end)

    return merged_intervals