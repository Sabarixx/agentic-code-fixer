from typing import List

def search(nums: List[int], target: int) -> int:
    """
    Search for target in a rotated sorted array of distinct integers.

    Parameters
    ----------
    nums : List[int]
        Rotated sorted array.
    target : int
        Value to search for.

    Returns
    -------
    int
        Index of target if found, otherwise -1.
    """
    if not nums:
        return -1

    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        mid_val = nums[mid]
        if mid_val == target:
            return mid

        # Determine which half is sorted
        if nums[left] <= mid_val:  # left half sorted
            if nums[left] <= target < mid_val:
                right = mid - 1
            else:
                left = mid + 1
        else:  # right half sorted
            if mid_val < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1