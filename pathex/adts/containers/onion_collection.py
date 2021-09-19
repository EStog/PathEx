from __future__ import annotations

import sys
from collections import deque
from collections.abc import Collection, Iterator, Reversible
from dataclasses import dataclass, field
from typing import Generic, Iterable, TypeVar

from pathex.adts.singleton import singleton

__all__ = ['OnionCollection', 'EmptyOnionCollection', 'NonemptyOnionCollection']

_E = TypeVar('_E')


def from_iterable(it: Iterable[_E]) -> OnionCollection[_E]:
    c = EmptyOnionCollection()
    for e in it:
        c = NonemptyOnionCollection(c, e)
    return c


class OnionCollection(Collection, Reversible, Generic[_E]):
    """Abstract base class for collections thar are immutable, recursive, hashable, and reversible.
    """


@singleton
@dataclass(frozen=True)
class EmptyOnionCollection(OnionCollection[_E]):
    """The instance of this class is an empty collection that can be used to construct new :class:`NonemptyOnionCollection` objects.
    """

    def __len__(self) -> int:
        return 0

    def __contains__(self, __x: object) -> bool:
        return False

    def __iter__(self) -> Iterator[_E]:
        return iter(())

    __reversed__ = __iter__

    # def __hash__(self):
    #     pass


@dataclass(frozen=True)
class NonemptyOnionCollection(OnionCollection[_E]):
    """This class represents an immutable collection that can be extended by recursively constructing new collections of this type.

    .. testsetup::

       from pathex.adts.containers.onion_collection import NonemptyOnionCollection, EmptyOnionCollection, from_iterable

    >>> c = NonemptyOnionCollection(EmptyOnionCollection(), 3)
    >>> assert list(c) == [3]
    >>> l = [1, 2, 3, 4]
    >>> c = from_iterable(l)
    >>> assert list(c) == l
    >>> assert 3 in c
    >>> assert '3' not in c
    >>> s = {c}
    >>> c1 = from_iterable(l)
    >>> assert c == c1
    >>> assert len(c) == len(c1) == len(l)
    >>> assert c1 in s
    >>> assert 4 not in EmptyOnionCollection()
    >>> assert list(EmptyOnionCollection()) == []
    """
    parent: OnionCollection[_E]
    last: _E
    _hash: int = field(init=False, repr=False)
    _len: int = field(init=False, repr=False)

    _HASH_BASE = 2
    _MAX_NUMBER = sys.maxsize

    def __post_init__(self):
        object.__setattr__(self, '_hash', hash(self.last) * self._power())
        object.__setattr__(self, '_len', len(self.parent) + 1)

    def __len__(self) -> int:
        return self._len

    def __reversed__(self) -> Iterator[_E]:
        def get_it():
            current = self
            while isinstance(current, NonemptyOnionCollection):
                yield current.last
                current = current.parent
        return get_it()

    def __iter__(self) -> Iterator[_E]:
        l = deque()
        for x in self.__reversed__():
            l.appendleft(x)
        return iter(l)

    def __hash__(self) -> int:
        return self._hash

    def __contains__(self, x: object) -> bool:
        for e in self.__reversed__():
            if e == x:
                return True

        return False

    def _power(self):
        return len(self.parent)*self._HASH_BASE % self._MAX_NUMBER
