from __future__ import annotations
from typing import Optional

def reverse_list(head: Optional["ListNode"]) -> Optional["ListNode"]:
    """
    Reverse a singly linked list in place and return the new head.

    Parameters
    ----------
    head : ListNode | None
        The head of the singly linked list to reverse.

    Returns
    -------
    ListNode | None
        The new head of the reversed list, or None if the input list was empty.
    """
    prev: Optional["ListNode"] = None
    current: Optional["ListNode"] = head

    while current is not None:
        nxt = current.next          # type: ignore[attr-defined]
        current.next = prev         # type: ignore[attr-defined]
        prev = current
        current = nxt

    return prev