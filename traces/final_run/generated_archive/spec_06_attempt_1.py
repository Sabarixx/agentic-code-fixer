from typing import List

def search(nums: List[int], target: int) -> int:
    """
    Search for target in a rotated sorted array of distinct integers.
    Returns the index of target if found, otherwise -1.
    """
    if not nums:
        return -1

    low, high = 0, len(nums) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_val = nums[mid]
        if mid_val == target:
            return mid

        # Determine which side is sorted
        if nums[low] <= mid_val:  # left side sorted
            if nums[low] <= target < mid_val:
                high = mid - 1
            else:
                low = mid + 1
        else:  # right side sorted
            if mid_val < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1

    return -1