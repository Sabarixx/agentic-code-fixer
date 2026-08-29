from typing import List

def search(nums: List[int], target: int) -> int:
    """
    Search for a target value in a rotated sorted array of distinct integers.

    Parameters
    ----------
    nums : List[int]
        Rotated sorted array of unique integers.
    target : int
        Value to search for.

    Returns
    -------
    int
        Index of target in nums if found, otherwise -1.

    Complexity
    ----------
    Time: O(log n)
    Space: O(1)
    """
    if not nums:
        return -1

    left, right = 0, len(nums) - 1

    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid

        # Determine which side is properly sorted
        if nums[left] <= nums[mid]:  # left side is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:  # right side is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1