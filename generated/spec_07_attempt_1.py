from typing import Dict, Optional

class LRUCache:
    class _Node:
        __slots__ = ("key", "value", "prev", "next")
        def __init__(self, key: int = 0, value: int = 0):
            self.key: int = key
            self.value: int = value
            self.prev: Optional["LRUCache._Node"] = None
            self.next: Optional["LRUCache._Node"] = None

    def __init__(self, capacity: int) -> None:
        self.capacity: int = capacity
        self.cache: Dict[int, LRUCache._Node] = {}
        self.size: int = 0

        # Dummy head and tail nodes to avoid edge checks
        self.head: LRUCache._Node = self._Node()
        self.tail: LRUCache._Node = self._Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_to_head(self, node: "LRUCache._Node") -> None:
        """Insert node right after head."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: "LRUCache._Node") -> None:
        """Detach node from its neighbors."""
        prev_node = node.prev
        next_node = node.next
        if prev_node is not None:
            prev_node.next = next_node
        if next_node is not None:
            next_node.prev = prev_node

    def _move_to_head(self, node: "LRUCache._Node") -> None:
        """Move an existing node to the head."""
        self._remove_node(node)
        self._add_to_head(node)

    def _pop_tail(self) -> "LRUCache._Node":
        """Remove and return the node just before the tail."""
        node = self.tail.prev
        if node is None or node is self.head:
            raise RuntimeError("Attempting to pop from an empty cache")
        self._remove_node(node)
        return node

    def get(self, key: int) -> int:
        node = self.cache.get(key)
        if node is None:
            return -1
        self._move_to_head(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if self.capacity == 0:
            return

        node = self.cache.get(key)
        if node:
            node.value = value
            self._move_to_head(node)
        else:
            new_node = self._Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            self.size += 1

            if self.size > self.capacity:
                tail = self._pop_tail()
                del self.cache[tail.key]
                self.size -= 1