from typing import List

def search(nums: List[int], target: int) -> int:
    """
    Search for target in a rotated sorted array of distinct integers.
    Returns the index of target if found, otherwise -1.
    Implements O(log n) binary search.
    """
    if not nums:
        return -1

    left, right = 0, len(nums) - 1

    while left <= right:
        mid = (left + right) // 2
        mid_val = nums[mid]

        if mid_val == target:
            return mid

        # Determine which side is properly sorted
        if nums[left] <= mid_val:  # left side is sorted
            if nums[left] <= target < mid_val:
                right = mid - 1
            else:
                left = mid + 1
        else:  # right side is sorted
            if mid_val < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1