from collections import OrderedDict
from typing import Dict

class LRUCache:
    """
    Least Recently Used (LRU) cache implementation with O(1) average time complexity
    for get and put operations.

    Attributes
    ----------
    capacity : int
        Maximum number of items the cache can hold.
    cache : OrderedDict[int, int]
        Ordered dictionary storing key-value pairs. The order represents
        usage recency, with the most recently used item at the end.
    """

    def __init__(self, capacity: int) -> None:
        """
        Initialize the LRU cache with a given capacity.

        Parameters
        ----------
        capacity : int
            The maximum number of key-value pairs the cache can store.
        """
        self.capacity: int = capacity
        self.cache: OrderedDict[int, int] = OrderedDict()

    def get(self, key: int) -> int:
        """
        Retrieve the value associated with the given key from the cache.

        If the key exists, it is marked as most recently used.
        If the key does not exist, return -1.

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
        # Move the key to the end to mark it as recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        """
        Insert or update the value for a given key in the cache.

        If the key already exists, its value is updated and it is marked as
        most recently used. If the key does not exist and the cache is at
        capacity, the least recently used item is evicted before insertion.

        Parameters
        ----------
        key : int
            The key to insert or update.
        value : int
            The value associated with the key.
        """
        if key in self.cache:
            # Update existing key and mark as recently used
            self.cache.move_to_end(key)
            self.cache[key] = value
            return

        if len(self.cache) >= self.capacity:
            # Evict least recently used item (first item in OrderedDict)
            self.cache.popitem(last=False)

        # Insert new key-value pair
        self.cache[key] = value