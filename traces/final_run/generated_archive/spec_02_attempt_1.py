from __future__ import annotations
from typing import Optional

class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Reverse a singly linked list in place.

    Parameters
    ----------
    head : Optional[ListNode]
        The head of the singly linked list to reverse.

    Returns
    -------
    Optional[ListNode]
        The new head of the reversed list, or None if the input list was empty.
    """
    prev: Optional[ListNode] = None
    curr: Optional[ListNode] = head

    while curr is not None:
        next_node: Optional[ListNode] = curr.next
        curr.next = prev
        prev = curr
        curr = next_node

    return prev