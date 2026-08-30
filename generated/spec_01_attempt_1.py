from typing import List, Dict

def two_sum(nums: List[int], target: int) -> List[int]:
    """
    Return indices of the two numbers in nums that add up to target.

    Parameters
    ----------
    nums : List[int]
        List of integers.
    target : int
        Target sum.

    Returns
    -------
    List[int]
        Two indices whose values sum to target. Order is arbitrary.

    Notes
    -----
    Exactly one solution exists. The function runs in O(n) time and O(n) space.
    """
    index_map: Dict[int, int] = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in index_map:
            return [index_map[complement], i]
        index_map[num] = i
    # The problem guarantees a solution, so this line should never be reached.
    raise ValueError("No two sum solution found")