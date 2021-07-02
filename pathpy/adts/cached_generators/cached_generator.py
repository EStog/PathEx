from __future__ import annotations

from enum import Enum
from functools import partial, update_wrapper
from typing import (Any, Callable, Collection, Generic, NamedTuple, Optional,
                    TypeVar)

from pathpy.adts.containers.queue_set import QueueSet

from .cached_iterator import CachedIterator
from .type_defs import TCacheType, TDecorableGenerator

_E_co = TypeVar('_E_co', covariant=True)
_E = TypeVar('_E')


class CacheType(NamedTuple):
    kind: type = QueueSet
    cache_add_op: Callable[[Collection, object], Any] = QueueSet.append

# TODO: Cache taking into account only some arguments.


class CachedGenerator(Generic[_E_co]):
    """This class wraps a generator and cache its results. See the examples.
    Designed for single-thread and deterministic generators only.

    The class can be used as a function decorator:

    >>> @cached_generator
    ... def f(o):
    ...     for x in o:
    ...         yield x

    A call to ``next``, saves the already generated values. You will
    then get an interator with the cached values, once you call the
    function generator again:

    >>> l = (1, 2, 3, 3, 3, 4, 4, 4)
    >>> it = f(l)
    >>> x, y = next(it), next(it)
    >>> assert it.cached_values == (x, y)
    >>> it = f(l)
    >>> assert it.cached_values == (x, y)
    >>> assert (x, y) == (next(it), next(it))
    >>> s = {x for x in it}
    >>> assert it.cached_values == QueueSet(l)
    >>> it = f(l)
    >>> it = it.skipped_cached_values()
    >>> try:
    ...     next(it)
    ... except StopIteration:
    ...     pass
    ... else:
    ...     print('wrong!')

    A call to a new object, will return an iterator without cached
    values, but a call, using the previous object will return an
    iterator with the previous cached objects:

    >>> it = f((1, 2, 3))
    >>> assert it.cached_values == ()
    >>> it = f(l)
    >>> assert it.cached_values == QueueSet(l)
    """

    def __init__(self, function: TDecorableGenerator[_E_co],
                 cache_type: CacheType = CacheType(),
                 non_repeated=None):
        self._cache_type = cache_type
        self._cache: TCacheType[_E_co] = dict()
        self._non_repeated = non_repeated
        update_wrapper(self, function)
        self.__wrapped__: TDecorableGenerator[_E_co]

    @property
    def cache_type(self):
        return self._cache_type

    def __call__(self, *args, **kwargs) -> CachedIterator[_E_co]:
        cache_entry = self._cache.get((self._cache_type, args), None)
        if cache_entry is None:
            cache_entry = (self._cache_type.kind(),
                           self.__wrapped__(*args, **kwargs))
            self._cache[(self._cache_type, args)] = cache_entry
        return CachedIterator(*cache_entry, self._cache_type.cache_add_op, self._non_repeated)


def new_cached_generator(
        cached_generator_type: type[CachedGenerator],
        function: Optional[TDecorableGenerator[_E]],
        cache_type: CacheType, non_repeated: bool) -> CachedGenerator[_E] | partial:
    if function is None:
        return partial(cached_generator_type, cache_type=cache_type, non_repeated=non_repeated)
    else:
        assert isinstance(function, Callable), 'function must be callable'
        assert isinstance(cache_type, CacheType), \
            'collection_type must be a creator of an instance of Sequence or Set'
        return cached_generator_type(function, cache_type, non_repeated)


def cached_generator(
        function: Optional[TDecorableGenerator[_E]] = None, /, *,
        cache_type: CacheType = CacheType(), non_repeated=None
) -> CachedGenerator[_E] | partial:
    return new_cached_generator(CachedGenerator, function, cache_type, non_repeated)


__all__ = ['CachedGenerator', 'CacheType',
           'new_cached_generator', 'cached_generator']
