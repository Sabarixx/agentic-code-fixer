from collections import OrderedDict
from typing import Dict

class LRUCache:
    """
    Least Recently Used (LRU) cache implementation with O(1) average time complexity
    for get and put operations.

    Attributes
    ----------
    capacity : int
        Maximum number of key-value pairs the cache can hold.
    cache : OrderedDict[int, int]
        Ordered dictionary storing key-value pairs in order of usage.
    """

    def __init__(self, capacity: int) -> None:
        """
        Initialize the LRU cache with a given capacity.

        Parameters
        ----------
        capacity : int
            The maximum number of items the cache can store.
        """
        self.capacity: int = capacity
        self.cache: OrderedDict[int, int] = OrderedDict()

    def get(self, key: int) -> int:
        """
        Retrieve the value associated with the given key if present in the cache.
        Marks the key as recently used.

        Parameters
        ----------
        key : int
            The key to look up.

        Returns
        -------
        int
            The value associated with the key, or -1 if the key is not present.
        """
        if key not in self.cache:
            return -1
        # Move key to the end to mark it as recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        """
        Insert or update the value for a key in the cache.
        If the cache exceeds its capacity, evict the least recently used item.

        Parameters
        ----------
        key : int
            The key to insert or update.
        value : int
            The value to associate with the key.
        """
        if key in self.cache:
            # Update existing key and mark as recently used
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            # Insert new key
            if len(self.cache) >= self.capacity:
                # Evict least recently used item (first item)
                self.cache.popitem(last=False)
            self.cache[key] = value