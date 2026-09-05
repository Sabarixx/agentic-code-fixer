from typing import List

def search(nums: List[int], target: int) -> int:
    """
    Search for target in a rotated sorted array of distinct integers.
    Returns the index of target if found, otherwise -1.
    Implements binary search in O(log n) time.
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