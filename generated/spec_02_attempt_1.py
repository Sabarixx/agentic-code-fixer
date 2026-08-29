from __future__ import annotations
from typing import Optional

class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

def reverse_list(head: ListNode | None) -> ListNode | None:
    """
    Reverse a singly linked list in place and return the new head.
    """
    prev: ListNode | None = None
    curr = head
    while curr is not None:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev