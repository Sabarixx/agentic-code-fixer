from typing import List

def merge(intervals: List[List[int]]) -> List[List[int]]:
    """
    Merge all overlapping or adjacent intervals in the input list.

    Parameters
    ----------
    intervals : List[List[int]]
        A list of intervals where each interval is represented as [start, end].

    Returns
    -------
    List[List[int]]
        A list of merged, non‑overlapping intervals covering all points in the input.

    Notes
    -----
    - Intervals that touch at endpoints (e.g., [1, 4] and [4, 5]) are merged.
    - The function does not modify the original input list.
    - Handles empty input gracefully by returning an empty list.
    """
    if not intervals:
        return []

    # Sort intervals by start (and by end for stability)
    sorted_intervals = sorted(intervals, key=lambda x: (x[0], x[1]))

    merged: List[List[int]] = []
    for start, end in sorted_intervals:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    return merged