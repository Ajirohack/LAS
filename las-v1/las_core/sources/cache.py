import time
from collections import OrderedDict
import json

class LRUCache:
    def __init__(self, capacity: int = 100, ttl: int = 3600):
        """
        Initialize LRU Cache.
        :param capacity: Maximum number of items to store.
        :param ttl: Time to live in seconds.
        """
        self.cache = OrderedDict()
        self.capacity = capacity
        self.ttl = ttl

    def _make_key(self, key):
        """Convert list/dict keys to hashable JSON string."""
        if isinstance(key, (list, dict)):
            return json.dumps(key, sort_keys=True)
        return key

    def get(self, key):
        """Get item from cache if exists and not expired."""
        key = self._make_key(key)
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        if time.time() - timestamp > self.ttl:
            self.cache.pop(key)
            return None
        
        self.cache.move_to_end(key)
        return value

    def put(self, key, value):
        """Add item to cache."""
        key = self._make_key(key)
        if key in self.cache:
            self.cache.move_to_end(key)
        
        self.cache[key] = (value, time.time())
        
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def clear(self):
        self.cache.clear()
