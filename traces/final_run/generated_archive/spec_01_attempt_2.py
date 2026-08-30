from typing import List, Dict

def two_sum(nums: List[int], target: int) -> List[int]:
    """
    Return the indices of the two distinct numbers in *nums* that sum to *target*.

    The function assumes that exactly one such pair exists and that an element
    cannot be used twice.  It raises a :class:`ValueError` if no pair is found,
    which should never happen under the problem constraints.
    """
    # Maps a number to its index in the list.
    index_by_value: Dict[int, int] = {}

    for current_index, current_value in enumerate(nums):
        needed = target - current_value
        if needed in index_by_value:
            return [index_by_value[needed], current_index]
        index_by_value[current_value] = current_index

    # This point is unreachable if the input satisfies the problem guarantees.
    raise ValueError("No two-sum solution found")