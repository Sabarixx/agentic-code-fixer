from __future__ import annotations
from typing import Optional

class ListNode:
    """Node of a singly linked list."""
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Reverse a singly linked list in place.

    Parameters
    ----------
    head : Optional[ListNode]
        The head of the list to reverse.

    Returns
    -------
    Optional[ListNode]
        The new head of the reversed list, or None if the input list was empty.
    """
    prev_node: Optional[ListNode] = None
    current_node: Optional[ListNode] = head

    while current_node is not None:
        next_node: Optional[ListNode] = current_node.next
        current_node.next = prev_node
        prev_node = current_node
        current_node = next_node

    return prev_node