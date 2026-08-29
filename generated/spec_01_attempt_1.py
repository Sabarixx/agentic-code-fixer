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
        is not specified.

    Raises
    ------
    ValueError
        If the input list has fewer than two elements.

    Notes
    -----
    The function assumes exactly one valid pair exists. It uses a hash map to
    achieve O(n) time and O(n) space complexity.
    """
    if len(nums) < 2:
        raise ValueError("Input list must contain at least two elements.")

    seen = {}
    for idx, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], idx]
        seen[num] = idx

    # The problem guarantees a solution, so this line should never be reached.
    raise RuntimeError("No valid pair found, despite problem constraints.")