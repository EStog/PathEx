from __future__ import annotations

from collections.abc import Iterator as Iter
from copy import copy
from typing import Iterable, Iterator, TypeVar

from pathex.adts.collection_wrapper import get_collection_wrapper

__doc__ = f"""

Useful functions and constants
==============================

:Module: ``{__name__}``

.. sectionauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>
.. codeauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>

---------------------------------------------------------------

This module contains some useful little functions and constants.

.. include:: ../non_essential_disclamer.txt
"""


__all__ = ['take', 'get_head_tail', 'SET_OF_TUPLES', 'SET_OF_STRS']

T = TypeVar('T')


def take(n: int, iterable: Iterable[T]) -> Iterator[T]:
    """take(n: int, iterable: Iterable[T]) -> Iterator[T]
    Returns an iterator that takes ``n`` elements from ``iterable``.

    If ``iterable`` has less than ``n`` elements, all elements from ``iterable`` are given.

    .. testsetup::

       from pathex.adts.util import take

    Example:

    >>> assert list(take(5, range(7))) == [0, 1, 2, 3, 4]
    >>> assert list(take(5, range(4))) == [0, 1, 2, 3]

    :param int n: the amount of elements to be taken.
    :param Iterable[T] it: the iterable to be taken from.
    :return: The resulting iterator.
    :rtype: Iterator[T]
    """
    return (x for _, x in zip(range(n), iterable))


def get_head_tail(iterable: Iterable[T]) -> tuple[object, Iterator[T] | None]:
    """Decompose the given ``iterable`` into its head and tail.

    .. testsetup::

       from pathex.adts.util import get_head_tail

    Example:

    >>> head, tail = get_head_tail([1, 2, 3, 4])
    >>> assert head == 1
    >>> assert list(tail) == [2, 3, 4]

    :param Iterable[T] iterable: The iterable to be decomposed. If it is an iterator it must also be :mod:`copiable <copy>`.
    :return: A tuple ``(head, tail)`` where ``head`` is the first element and ``tail`` is the rest of the iterable.
    :rtype: tuple[object, Iterator[T] | None]
    """

    if isinstance(iterable, Iter):
        # must be copiable. Standard generators are NOT copiable.
        it = copy(iterable)
    else:
        it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        return None, None
    else:
        return first, it


SET_OF_TUPLES = get_collection_wrapper(set, put=lambda s, w: s.add(tuple(w)))
SET_OF_TUPLES.__doc__ = """A :class:`~.CollectionWrapper` where elements given to :meth:`~.put` are converted to :class:`tuple` before addition."""


SET_OF_STRS = get_collection_wrapper(
    set, put=lambda s, w: s.add(''.join(str(l) for l in w)))
SET_OF_STRS.__doc__ = """A :class:`~.CollectionWrapper` where elements given to :meth:`~.put` are converted to :class:`str` before addition."""
