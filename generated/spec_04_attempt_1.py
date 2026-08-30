from typing import List

def merge(intervals: List[List[int]]) -> List[List[int]]:
    """
    Merge all overlapping intervals in the input list.

    Parameters
    ----------
    intervals : List[List[int]]
        A list of intervals where each interval is represented as [start, end].

    Returns
    -------
    List[List[int]]
        A list of merged, non-overlapping intervals covering all input intervals.

    Notes
    -----
    The function first sorts the intervals by their start times and then
    iteratively merges overlapping intervals. The overall time complexity is
    O(n log n) due to the sorting step, and the space complexity is O(n)
    for the output list.
    """
    if not intervals:
        return []

    # Sort intervals by start time
    intervals.sort(key=lambda x: x[0])

    merged: List[List[int]] = [intervals[0]]
    for current in intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:  # Overlap
            last[1] = max(last[1], current[1])
        else:
            merged.append(current)

    return merged