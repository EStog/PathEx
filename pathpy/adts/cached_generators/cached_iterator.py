from __future__ import annotations

from collections.abc import Iterator, Set
from typing import Any, Callable, Collection, Generic, TypeVar

from pathpy.adts.containers.queue_set import QueueSet

_T_co = TypeVar('_T_co', covariant=True)


class CachedIterator(Iterator[_T_co], Generic[_T_co]):
    def __init__(self, cached_values: Collection[_T_co],
                 iterator: Iterator[_T_co],
                 cache_add_op: Callable[[Collection, object], Any],
                 non_repeated=None):
        self._cached_values = cached_values
        self._iterator = iterator
        self._it = iter(self._cached_values)
        self._next = self._next_from_cached_values
        self._cache_add_op = cache_add_op
        self._non_repeated = non_repeated
        if non_repeated or (non_repeated is None and isinstance(cached_values, (Set, QueueSet))):
            self._get_next = self._get_while_not_in_cache
        else:
            self._get_next = next

    @property
    def cached_values(self) -> tuple[_T_co, ...]:
        if isinstance(self._cached_values, QueueSet):
            return self._cached_values.as_tuple()
        else:
            return tuple(self._cached_values)

    def __iter__(self):
        return self

    def __next__(self):
        return self._next()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._cached_values}, {self._iterator})'

    def _next_from_cached_values(self):
        try:
            return next(self._it)
        except StopIteration:
            self._next = self._next_from_generator
            return self._next_from_generator()

    def _get_while_not_in_cache(self, it: Iterator[_T_co]):
        x = next(it)
        while x in self._cached_values:
            x = next(it)
        return x

    def _next_from_generator(self):
        x = self._get_next(self._iterator)
        self._cache_add_op(self._cached_values, x)
        return x

    def skipped_cached_values(self):
        it = CachedIterator(self._cached_values, self._iterator,
                            self._cache_add_op, self._non_repeated)
        it._next = it._next_from_generator
        return it

    def restarted(self):
        return CachedIterator(self._cached_values, self._iterator,
                              self._cache_add_op, self._non_repeated)


__all__ = ['CachedIterator']
