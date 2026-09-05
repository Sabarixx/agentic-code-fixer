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
    - Exactly one solution is guaranteed.
    - The same element cannot be used twice.
    - If `nums` is empty or has fewer than two elements, an empty list is returned.
    """
    if len(nums) < 2:
        return []

    index_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in index_map:
            return [index_map[complement], i]
        index_map[num] = i

    # According to the problem statement, this line should never be reached.
    return []