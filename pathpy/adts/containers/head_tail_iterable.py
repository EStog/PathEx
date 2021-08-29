from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from pathpy.adts.util import get_head_tail
from typing import Iterator, TypeVar

from pathpy.adts.cached_generators.cached_iterator import CachedIterator

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
    >>> assert list(x.appended(4)) == [1, 2, 3, 4]
    >>> z = x.appended_left(3)
    >>> assert list(z) == [3, 1, 2, 3]
    >>> assert z.head == 3
    >>> assert list(z.tail) == list(x)
    >>> assert list(x.copy()) == list(x)
    >>> assert x.copy() is not x
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
        head, _tail = get_head_tail(iterable)
        self = object.__new__(cls)
        object.__setattr__(self, 'head', head)
        if _tail is None:
            _tail = iter(())
        object.__setattr__(self, '_tail', CachedIterator([], _tail, list.append))
        return self

    def __add__(self, other: HeadTailIterable):
        if not isinstance(other, HeadTailIterable):
            raise TypeError(
                f'can only concatenate {self.__class__.__name__} (not "{type(other)}") to {self.__class__.__name__}')
        if self.head and other.head:
            return self.__class__(chain([self.head], self._tail.restarted(),
                                        [other.head], other._tail.restarted()))
        elif self.head:
            return self.copy()
        elif other.head:
            return other.copy()
        else:
            return self.__class__(())

    def appended(self, other):
        if self.head:
            return self.__class__(chain([self.head], self._tail.restarted(), [other]))
        else:
            return self.__class__([other])

    def appended_left(self, other):
        if self.head:
            return self.__class__(chain([other, self.head], self._tail.restarted()))
        else:
            return self.__class__([other])

    @cached_property
    def tail(self) -> HeadTailIterable[_E]:
        return self.__class__(self._tail.restarted())

    def __iter__(self):
        return self.HeadTailIterator(self)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{tuple(self)}'

    def __copy__(self):
        obj = object.__new__(self.__class__)
        object.__setattr__(obj, 'head', self.head)
        object.__setattr__(obj, '_tail', self._tail.restarted())
        return obj

    def __eq__(self, other):
        if isinstance(other, HeadTailIterable):
            return list(self) == list(other)
        else:
            return False

    copy = __copy__
