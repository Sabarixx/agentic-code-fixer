from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ListNode:
    val: int = 0
    next: ListNode | None = None


def reverse_list(head: ListNode | None) -> ListNode | None:
    prev = None
    curr = head
    while curr is not None:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev


def from_list(values: list[int]) -> ListNode | None:
    dummy = ListNode()
    tail = dummy
    for value in values:
        tail.next = ListNode(value)
        tail = tail.next
    return dummy.next


def to_list(head: ListNode | None) -> list[int]:
    out: list[int] = []
    while head is not None:
        out.append(head.val)
        head = head.next
    return out
