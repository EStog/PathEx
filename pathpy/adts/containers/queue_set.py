from __future__ import annotations
from collections import deque

from collections.abc import Iterable
from typing import Collection, TypeVar

_T = TypeVar('_T')
_S = TypeVar('_S')


class QueueSet(Collection[_T]):
    """A set whose elements are keeped in FIFO (like in a queue) order"""

    def __new__(cls, queue=()) -> QueueSet[_T]:
        """
        >>> s = QueueSet([1, 2, 3, 4, 3, 5])
        >>> assert s.as_set() == {1, 2, 3, 4, 5}
        >>> assert s.as_tuple() == (1, 2, 3, 4, 5)
        """
        if isinstance(queue, QueueSet):
            return queue
        self = super().__new__(cls)
        self._queue = queue
        queue = deque()
        self._set = set()
        cls._set: set[_T]
        for x in self._queue:
            if x not in self._set:
                self._set.add(x)
                queue.append(x)
        self._queue = queue
        cls._queue: deque[_T]
        return self

    def as_tuple(self) -> tuple[_T, ...]:
        return tuple(self._queue)

    def as_set(self) -> frozenset[_T]:
        return frozenset(self._set)

    def __contains__(self, o: object) -> bool:
        return o in self._set

    def __iter__(self):
        return iter(self._queue)

    def add(self, element: _T) -> None:
        """
        >>> x = QueueSet()
        >>> l = [3, 5, 2, 5, 6, 6]
        >>> for e in l:
        ...     x.add(e)
        >>> assert x.as_set() == set(l)
        >>> assert x.as_tuple() == (3, 5, 2, 6)
        """
        if element not in self._set:
            self._set.add(element)
            self._queue.append(element)

    append = add

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Iterable):
            return self._queue == deque(other)
        else:
            return False

    def __len__(self):
        return len(self._queue)

    def __bool__(self):
        return self._set != set()

    def __str__(self):
        return f'{self.__class__.__name__}({self._queue})'

    def pop(self) -> _T:
        """
        >>> l = [1, 2, 3, 4]
        >>> x = QueueSet(l)
        >>> l1 = []
        >>> while x:
        ...     l1.append(x.pop())
        >>> assert l == l1
        """
        x = self._queue.popleft()
        self._set.remove(x)
        return x


__all__ = ['QueueSet']
