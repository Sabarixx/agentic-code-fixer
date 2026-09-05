from typing import Dict, List

def two_sum(nums: List[int], target: int) -> List[int]:
    """
    Find two distinct indices i, j such that nums[i] + nums[j] == target.

    Parameters
    ----------
    nums : List[int]
        List of integers to search.
    target : int
        The desired sum of two distinct elements.

    Returns
    -------
    List[int]
        A list containing the two indices that form the target sum.
        The function assumes exactly one solution exists.
    """
    seen_indices: Dict[int, int] = {}
    for current_index, value in enumerate(nums):
        needed = target - value
        if needed in seen_indices:
            return [seen_indices[needed], current_index]
        seen_indices[value] = current_index

    # The problem guarantees a solution, so this line is never reached.
    return []