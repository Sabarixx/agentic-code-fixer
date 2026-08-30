from typing import Dict, List

def two_sum(nums: List[int], target: int) -> List[int]:
    """
    Find two indices in *nums* whose values sum to *target*.

    Parameters
    ----------
    nums : List[int]
        List of integers to search.
    target : int
        Desired sum of two elements.

    Returns
    -------
    List[int]
        The indices of the two numbers that add up to *target*.
        The order of the indices is not significant.

    Notes
    -----
    Exactly one solution is guaranteed. The function runs in O(n) time
    and uses O(n) additional space.
    """
    seen_indices: Dict[int, int] = {}
    for idx, value in enumerate(nums):
        needed = target - value
        if needed in seen_indices:
            return [seen_indices[needed], idx]
        seen_indices[value] = idx

    # The problem statement guarantees a solution, so this should never happen.
    raise ValueError("No two-sum solution found")