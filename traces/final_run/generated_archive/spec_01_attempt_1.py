from typing import List

def two_sum(nums: List[int], target: int) -> List[int]:
    """
    Return indices of the two numbers in nums that add up to target.
    Assumes exactly one solution exists and the same element cannot be used twice.
    """
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    # The problem guarantees a solution, so this line should never be reached.
    raise ValueError("No two sum solution found")