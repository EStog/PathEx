from __future__ import annotations

from functools import partial, wraps
from typing import Optional, TypeVar

from pathpy.adts.collection_wrapper import (CollectionWrapper,
                                            get_collection_wrapper)
from pathpy.adts.containers.queue_set import QueueSet

from .cached_generator import CachedGenerator, new_cached_generator
from .type_defs import TDecorableDescriptorGenerator, TDecorableGenerator

__all__ = ['CachedGeneratorMethod', 'cached_generator_method']

_E_co = TypeVar('_E_co', covariant=True)
_E = TypeVar('_E')


class CachedGeneratorMethod(CachedGenerator[_E_co]):
    """
    >>> class A:
    ...     @cached_generator_method(cache_type= get_collection_wrapper(list, put=list.append))
    ...     def f(self, o):
    ...         for x in o:
    ...             yield x

    >>> l = (2, 3, 4, 5, 5, 5)
    >>> a = A()
    >>> it = a.f(l)
    >>> assert (2, 3) == (next(it), next(it))
    >>> it = a.f(l)
    >>> it = it.skipped_cached_values()
    >>> s = [x for x in it]
    >>> assert s == [4, 5, 5, 5]
    >>> assert it.cached_values == l
    """

    def __init__(self, function: TDecorableDescriptorGenerator[_E_co],
                 cache_type: CollectionWrapper = get_collection_wrapper(QueueSet, put=QueueSet.append), non_repeated=None):
        super().__init__(function, cache_type, non_repeated)
        self.__isabstractmethod__ = \
            getattr(function, '__isabstractmethod__', False)

    def __get__(self, obj, cls=None):
        @wraps(self)
        def f(*args, **kwargs):
            return self(obj, *args, **kwargs)

        if obj is None:
            return self
        else:
            return f


def cached_generator_method(
        function: Optional[TDecorableGenerator[_E]] = None, /, *,
        cache_type: CollectionWrapper = get_collection_wrapper(QueueSet, put=QueueSet.append), non_repeated=None) -> CachedGenerator[_E] | partial:
    return new_cached_generator(CachedGeneratorMethod, function, cache_type, non_repeated)
