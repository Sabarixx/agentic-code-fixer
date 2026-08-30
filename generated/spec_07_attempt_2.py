from __future__ import annotations

from typing import Dict, Optional


class LRUCache:
    """Least‑Recently‑Used cache with O(1) `get` and `put` operations.

    Parameters
    ----------
    capacity : int
        Maximum number of key/value pairs the cache can hold.
    """

    class _Node:
        """Doubly‑linked list node used internally by :class:`LRUCache`."""
        __slots__ = ("key", "value", "prev", "next")

        def __init__(self, key: int = 0, value: int = 0) -> None:
            self.key: int = key
            self.value: int = value
            self.prev: Optional["LRUCache._Node"] = None
            self.next: Optional["LRUCache._Node"] = None

    def __init__(self, capacity: int) -> None:
        self._capacity: int = capacity
        self._cache: Dict[int, LRUCache._Node] = {}

        # Dummy head and tail nodes simplify edge‑case handling.
        self._head: LRUCache._Node = self._Node()
        self._tail: LRUCache._Node = self._Node()
        self._head.next = self._tail
        self._tail.prev = self._head

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _remove_node(self, node: _Node) -> None:
        """Detach *node* from the doubly‑linked list."""
        prev_node, next_node = node.prev, node.next
        assert prev_node is not None and next_node is not None  # for type checkers
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_node_to_front(self, node: _Node) -> None:
        """Insert *node* immediately after the dummy head (most recent)."""
        node.next = self._head.next
        node.prev = self._head
        self._head.next.prev = node
        self._head.next = node

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def get(self, key: int) -> int:
        """Return the value for *key* if present, otherwise ``-1``.

        The accessed key is marked as most recently used.
        """
        node = self._cache.get(key)
        if node is None:
            return -1

        self._remove_node(node)
        self._add_node_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """Insert or update the value for *key*.

        If the cache exceeds its capacity, the least recently used item
        is evicted.
        """
        if self._capacity == 0:
            return

        node = self._cache.get(key)
        if node:
            node.value = value
            self._remove_node(node)
            self._add_node_to_front(node)
            return

        if len(self._cache) >= self._capacity:
            # Evict the least recently used node (just before the dummy tail).
            lru_node = self._tail.prev
            assert lru_node is not None and lru_node.prev is not None
            self._remove_node(lru_node)
            del self._cache[lru_node.key]

        new_node = self._Node(key, value)
        self._cache[key] = new_node
        self._add_node_to_front(new_node)