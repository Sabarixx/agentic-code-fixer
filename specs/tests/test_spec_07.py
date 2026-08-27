from specs.reference.spec_07 import LRUCache


def test_lru_leetcode_sequence():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(3, 3)
    assert cache.get(2) == -1
    cache.put(4, 4)
    assert cache.get(1) == -1
    assert cache.get(3) == 3
    assert cache.get(4) == 4


def test_lru_update_existing_key():
    cache = LRUCache(1)
    cache.put(1, 10)
    cache.put(1, 20)
    assert cache.get(1) == 20


def test_lru_get_refreshes_recency():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(3, 3)
    assert cache.get(1) == 1
    assert cache.get(2) == -1


def test_lru_missing_key():
    cache = LRUCache(2)
    assert cache.get(99) == -1


def test_lru_capacity_one_evicts():
    cache = LRUCache(1)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == -1
    assert cache.get(2) == 2
