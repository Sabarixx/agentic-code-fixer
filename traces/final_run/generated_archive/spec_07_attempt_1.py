from typing import Optional

class LRUCache:
    """Least Recently Used (LRU) cache implementation with O(1) get and put operations."""

    class _Node:
        __slots__ = ("key", "value", "prev", "next")

        def __init__(self, key: int = 0, value: int = 0):
            self.key: int = key
            self.value: int = value
            self.prev: Optional["LRUCache._Node"] = None
            self.next: Optional["LRUCache._Node"] = None

    def __init__(self, capacity: int) -> None:
        self.capacity: int = capacity
        self.cache: dict[int, LRUCache._Node] = {}
        # Dummy head and tail nodes to avoid edge checks
        self.head: LRUCache._Node = self._Node()
        self.tail: LRUCache._Node = self._Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: _Node) -> None:
        """Detach node from the linked list."""
        prev_node, next_node = node.prev, node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: _Node) -> None:
        """Insert node right after head (most recently used)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if self.capacity == 0:
            return
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                # Evict least recently used (node before tail)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            new_node = self._Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)