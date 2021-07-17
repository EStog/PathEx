from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from typing import Iterator, TypeVar

from pathpy.adts.cached_generators.cached_iterator import CachedIterator

_E = TypeVar('_E')


@dataclass(frozen=True, init=False)
class HeadTailIterable(Iterable[_E]):
    """An iterable with head and tail.

    >>> x = HeadTailIterable.new([2, 3, 4, 5])
    >>> assert x.head == 2
    >>> assert list(x.tail) == [3, 4, 5]
    >>> assert [2, 3, 4, 5] == [e for e in x]
    >>> assert [2, 3, 4, 5] == [e for e in x]

    >>> s = {2, 3, 4}
    >>> x = HeadTailIterable.new(s)
    >>> first = next(iter(s))
    >>> rest = s - {first}
    >>> assert x.head == first
    >>> assert set(x.tail) == set(rest)
    >>> assert [2, 3, 4] == [e for e in x]
    >>> assert s == {2, 3, 4}

    >>> it = iter([1, 2, 3, 4])
    >>> x = HeadTailIterable.new(it)
    >>> assert x.head == 1
    >>> assert [e for e in x.tail] == [2, 3, 4]
    >>> assert [1, 2, 3, 4] == [e for e in x]

    >>> x = HeadTailIterable.new([1])
    >>> assert x.tail.head is None
    >>> x = HeadTailIterable.new([])
    >>> assert x.head is None and x.tail.head is None

    An interable of this type may be expanded.

    >>> h = HeadTailIterable.new([])
    >>> assert h.head is None
    >>> assert list(h.tail) == []
    >>> h.append(2)
    >>> assert h.head == 2
    >>> assert h.tail.head is None
    >>> h.append(3)
    >>> assert list(h.tail) == [3]
    """

    class ExtensibleTail(CachedIterator):
        def append(self, x):
            self._iterator = chain(self._iterator, (x,))

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
    _tail: ExtensibleTail

    @classmethod
    def new(cls, iterable) -> HeadTailIterable[_E]:
        if isinstance(iterable, HeadTailIterable):
            return iterable
        _tail = cls.ExtensibleTail(deque(), iter(iterable), deque.append)
        try:
            head = next(_tail)
        except StopIteration:
            head = None
        obj = HeadTailIterable.__new__(cls)
        object.__setattr__(obj, 'head', head)
        object.__setattr__(obj, '_tail', _tail)
        return obj

    def __init__(self, *args, **kwargs) -> None:
        raise TypeError('Do not use FunctionalIterable.__init__ directly.'
                        'Use FunctionalIterable.new instead')

    @cached_property
    def tail(self):
        return self.new(self._tail)

    def append(self, x: _E):
        self._tail.append(x)
        if self.head is None:
            object.__setattr__(self, 'head', x)
            next(self._tail)
        else:
            del self.__dict__['tail']

    def __iter__(self):
        return self.HeadTailIterator(self)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'


__all__ = ['HeadTailIterable']
