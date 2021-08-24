from collections.abc import Iterable, Iterator
from copy import copy

from pathpy.adts.collection_wrapper import get_collection_wrapper


def take(n, it):
    return (x for _, x in zip(range(n), it))


def get_first_rest(iterable: Iterable):
    if isinstance(iterable, Iterator):
        # <-- must be copiable. Standard generators are NOT copiable.
        it = copy(iterable)
    else:
        it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        return None, None
    else:
        return first, it


SET_OF_TUPLES = get_collection_wrapper(set, lambda s, w: s.add(tuple(w)))

SET_OF_STRS = get_collection_wrapper(
    set, lambda s, w: s.add(''.join(str(l) for l in w)))
