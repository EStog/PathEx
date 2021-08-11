from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from typing import Iterator, TypeVar

from pathpy.adts.cached_generators.cached_iterator import CachedIterator
from copy import copy

__all__ = ['HeadTailIterable']

_E = TypeVar('_E')


@dataclass(frozen=True, init=False)
class HeadTailIterable(Iterable[_E]):
    """An iterable with head and tail.

    >>> x = HeadTailIterable([2, 3, 4, 5])
    >>> assert x.head == 2
    >>> assert list(x.tail) == [3, 4, 5]
    >>> assert [2, 3, 4, 5] == list(x)
    >>> assert [2, 3, 4, 5] == [e for e in x]

    >>> s = {2, 3, 4}
    >>> x = HeadTailIterable(s)
    >>> first = next(iter(s))
    >>> rest = s - {first}
    >>> assert x.head == first
    >>> assert set(x.tail) == set(rest)
    >>> assert [2, 3, 4] == [e for e in x]
    >>> assert s == {2, 3, 4}

    >>> it = iter([1, 2, 3, 4])
    >>> x = HeadTailIterable(it)
    >>> assert x.head == 1
    >>> assert [e for e in x.tail] == [2, 3, 4]
    >>> assert [1, 2, 3, 4] == list(x)

    >>> x = HeadTailIterable([1])
    >>> assert x.tail.head is None
    >>> x = HeadTailIterable([])
    >>> assert x.head is None and x.tail.head is None

    HeadTailIterableObjects may be concatenated:

    >>> x = HeadTailIterable([1, 2, 3])
    >>> y = HeadTailIterable(['a', 'b'])
    >>> assert list(x + y) == [1, 2, 3, 'a', 'b']
    """

    class HeadTailIterator(Iterator):
        def __init__(self, iterable: HeadTailIterable) -> None:
            self._iterable = iterable

        def __next__(self):
            x = self._iterable.head
            if x is None:
                raise StopIteration
            self._iterable = self._iterable.tail
            return x

    head: _E | None
    _tail: CachedIterator

    def __new__(cls, iterable: Iterable[_E]) -> HeadTailIterable[_E]:
        if isinstance(iterable, HeadTailIterable):
            return iterable
        _tail = CachedIterator(deque(), iter(iterable), deque.append)
        try:
            head = next(_tail)
        except StopIteration:
            head = None
        self = object.__new__(cls)
        object.__setattr__(self, 'head', head)
        object.__setattr__(self, '_tail', _tail)
        return self

    def __add__(self, other: HeadTailIterable):
        if not isinstance(other, HeadTailIterable):
            raise TypeError(
                f'can only concatenate {self.__class__.__name__} (not "{type(other)}") to {self.__class__.__name__}')
        if self.head and other.head:
            return self.__class__(chain([self.head], self._tail, [other.head], other._tail))
        elif self.head:
            return copy(self)
        elif other.head:
            return copy(other)
        else:
            return self.__class__(())

    def appended(self, other):
        if self.head:
            return self.__class__(chain([self.head], self._tail, [other]))
        else:
            return self.__class__([other])

    @cached_property
    def tail(self) -> HeadTailIterable[_E]:
        return self.__class__(self._tail)

    def __iter__(self):
        return self.HeadTailIterator(self)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'
