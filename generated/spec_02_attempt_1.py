from typing import Optional

class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Reverse a singly linked list in place and return the new head.

    Args:
        head: The head of the singly linked list.

    Returns:
        The new head of the reversed list, or None if the input list is empty.
    """
    prev: Optional[ListNode] = None
    curr: Optional[ListNode] = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev