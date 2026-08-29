from typing import List

def two_sum(nums: List[int], target: int) -> List[int]:
    """
    Return indices of the two numbers in `nums` that add up to `target`.

    Parameters
    ----------
    nums : List[int]
        List of integers.
    target : int
        Target sum.

    Returns
    -------
    List[int]
        Two indices whose corresponding values sum to `target`. The order of indices
        is arbitrary.

    Notes
    -----
    The function assumes exactly one valid pair exists and does not use the same
    element twice. It runs in O(n) time and O(n) space.
    """
    index_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in index_map:
            return [index_map[complement], i]
        index_map[num] = i
    # The problem guarantees a solution, so this line should never be reached.
    raise ValueError("No valid pair found")