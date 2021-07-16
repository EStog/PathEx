from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from typing import TypeVar

from pathpy.adts.cached_generators.cached_iterator import CachedIterator

_E = TypeVar('_E')

# TODO: Dividir esta clase en dos: una que brinde la interfaz [first:rest] y la otra que maneje un iterable no iterador llevando la cuenta de la posición actual


@dataclass(frozen=True, init=False, repr=False)
class HeadTailIterable(Iterable[_E]):
    """An iterable with head and tail.

    >>> x = HeadTailIterable([2, 3, 4, 5])
    >>> assert x.head == 2
    >>> assert list(x.tail) == [3, 4, 5]
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
    >>> assert [1, 2, 3, 4] == [e for e in x]

    >>> x = HeadTailIterable([1])
    >>> assert not x.has_tail
    >>> x = HeadTailIterable([])
    >>> assert not x.has_head and not x.has_tail

    An interable of this type may be expanded.

    >>> h = HeadTailIterable([])
    >>> try:
    ...     h.head
    ... except AttributeError:
    ...     pass # Right!
    ... else:
    ...     print('Wrong!')

    >>> h.append(2)
    >>> assert h.head == 2

    >>> try:
    ...     h.tail
    ... except AttributeError:
    ...     pass # Right!
    ... else:
    ...     print('Wrong!')

    >>> h.append(3)
    >>> h.reset()
    >>> assert h.tail == 3

    """
    _iterable: Iterable[_E]

    def __new__(cls, iterable: Iterable[_E], taker=None) -> HeadTailIterable[_E]:
        assert isinstance(iterable, Iterable), \
            '`iterable` argument is not Iterable'
        if isinstance(iterable, HeadTailIterable):
            return iterable
        return super().__new__(cls)

    def __init__(self, iterable: Iterable[_E]):
        # if __new__ does not return an already existing object.
        if not hasattr(self, '_interable'):
            object.__setattr__(self, '_iterable', iterable)
            self._init()
            self._tail: CachedIterator[_E]

    @property
    def iterable(self):
        return self._iterable

    @cached_property
    def head(self) -> _E:
        it = iter(self._iterable)
        try:
            head = next(it)
        except StopIteration:
            raise AttributeError
        else:
            object.__setattr__(
                self, '_tail', CachedIterator([], it, list.append))
            return head

    @cached_property
    def tail(self) -> HeadTailIterable[_E] | _E:
        try:
            x = next(self._tail)
        except StopIteration:
            raise AttributeError
        else:
            try:
                next(self._tail)
            except StopIteration:
                return x
            else:
                return self.__class__(self._tail.restarted())

    @property
    def has_tail(self):
        return hasattr(self, 'tail')

    @property
    def has_head(self):
        return hasattr(self, 'head')

    def _init(self):
        try:
            self.head  # <-- This is for initialization
        except AttributeError:
            pass

    def _del(self, name):
        try:
            object.__delattr__(self, name)
        except AttributeError:
            pass
        try:
            object.__delattr__(self, f'has_{name}')
        except AttributeError:
            pass

    def _get(self, name):
        self._del(name)
        return getattr(self, name)

    def reset(self):
        self._del('head')
        self._del('tail')
        self._init()

    def append(self, x):
        h = ()
        if hasattr(self, 'head'):
            h = (self.head, self._tail)
        object.__setattr__(self, '_iterable', chain(h, (x,)))
        self.reset()

    def __iter__(self) -> Iterator:
        if hasattr(self, 'head'):
            return chain((self.head,), self._tail.restarted())
        else:
            return self._tail.restarted()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._iterable})'


__all__ = ['HeadTailIterable']
