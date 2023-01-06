from .db import User


class Cache:
    def __init__(self, _max=100):
        self._cache = []
        self._max = _max
    
    def add(self, item: int):
        self._cache.insert(0, item)
        if len(self._cache) > self._max:
            self._cache.pop()

    def clear(self):
        self._cache = []

    def __getitem__(self, index: int) -> User:
        self._cache.insert(0, self._cache.pop(index))
        return self._cache[index]

    def __contains__(self, item: User) -> bool:
        return item in self._cache

cache = Cache()
