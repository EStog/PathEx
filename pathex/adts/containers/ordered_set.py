from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from typing import Collection, TypeVar

__all__ = ['OrderedSet']

_T = TypeVar('_T')


class OrderedSet(Collection[_T]):
    """A set whose elements are ordered"""

    def __new__(cls, queue=()) -> OrderedSet[_T]:
        """

        .. testsetup::

           from pathex.adts.containers.ordered_set import OrderedSet

        >>> s = OrderedSet([1, 2, 3, 4, 3, 5])
        >>> assert s is OrderedSet(s)
        >>> assert s.as_set() == {1, 2, 3, 4, 5}
        >>> assert s.as_tuple() == (1, 2, 3, 4, 5)
        """
        if isinstance(queue, OrderedSet):
            return queue
        self = super().__new__(cls)
        cls._queue: deque[_T]
        cls._set: set[_T]
        self._queue = deque()
        self._set = set()
        for x in queue:
            self.append(x)
        return self

    def _add(self, element, add):
        if element not in self._set:
            self._set.add(element)
            add(element)

    def add(self, element: _T) -> None:
        """
        .. testsetup::

           from pathex.adts.containers.ordered_set import OrderedSet

        >>> x = OrderedSet()
        >>> l = [3, 5, 2, 5, 6, 6]
        >>> for e in l:
        ...     x.add(e)
        >>> assert x.as_set() == set(l)
        >>> assert x.as_tuple() == (3, 5, 2, 6)
        """
        self._add(element, self._queue.append)

    def addleft(self, element: _T) -> None:
        """
        .. testsetup::

           from pathex.adts.containers.ordered_set import OrderedSet

        >>> x = OrderedSet()
        >>> l = [3, 5, 2, 5, 6, 6]
        >>> for e in l:
        ...     x.addleft(e)
        >>> assert x.as_set() == set(l)
        >>> assert x.as_tuple() == (6, 2, 5, 3)
        """
        self._add(element, self._queue.appendleft)

    append = add
    appendleft = addleft

    def extend(self, other: Iterable[_T]):
        """
        .. testsetup::

           from pathex.adts.containers.ordered_set import OrderedSet


        >>> o = OrderedSet([1, 2, 3])
        >>> o.extend([3, 4, 5])
        >>> assert o.as_tuple() == (1, 2, 3, 4, 5)        """

        for e in other:
            self.append(e)

    def extendleft(self, other: Iterable[_T]):
        """
        .. testsetup::

           from pathex.adts.containers.ordered_set import OrderedSet


        >>> o = OrderedSet([1, 2, 3])
        >>> o.extendleft([3, 4, 5])
        >>> assert o.as_tuple() == (5, 4, 1, 2, 3)
        """
        for e in other:
            self.appendleft(e)

    update = append
    updateleft = appendleft

    def _pop(self, pop):
        try:
            x = pop()
        except IndexError:
            raise IndexError(f'pop from empty {self.__class__.__name__}')
        self._set.remove(x)
        return x

    def pop(self) -> _T:
        """
        .. testsetup::

           from pathex.adts.containers.ordered_set import OrderedSet

        >>> l = [1, 2, 3, 4]
        >>> x = OrderedSet(l)
        >>> l1 = []
        >>> while x:
        ...     l1.append(x.pop())
        >>> assert list(reversed(l)) == l1
        """
        return self._pop(self._queue.pop)

    def popleft(self) -> _T:
        """
        .. testsetup::

           from pathex.adts.containers.ordered_set import OrderedSet

        >>> l = [1, 2, 3, 4]
        >>> x = OrderedSet(l)
        >>> l1 = []
        >>> while x:
        ...     l1.append(x.popleft())
        >>> assert l == l1
        """
        return self._pop(self._queue.popleft)

    def as_tuple(self) -> tuple[_T, ...]:
        return tuple(self._queue)

    def as_set(self) -> frozenset[_T]:
        return frozenset(self._set)

    def __contains__(self, o: object) -> bool:
        return o in self._set

    def __iter__(self):
        return iter(self._queue)

    def __eq__(self, other: object) -> bool:
        """
        .. testsetup::

           from pathex.adts.containers.ordered_set import OrderedSet

        >>> l = [1, 2, 3, 4]
        >>> o = OrderedSet(l)
        >>> assert o == [1, 2, 3, 4]
        >>> assert o != [1, 2, 3, 4, 5]
        >>> assert o != 25
        """
        if isinstance(other, Iterable):
            return self._queue == deque(other)
        else:
            return False

    def __len__(self):
        return len(self._queue)

    def __bool__(self):
        return self._set != set()

    def __repr__(self): # pragma: no cover
        return f'{self.__class__.__name__}({self._queue})'
