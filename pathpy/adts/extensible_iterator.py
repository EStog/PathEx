from collections.abc import Iterator, Iterable
from itertools import chain

class ExtensibleIterator(Iterator):
    def __init__(self, iterable: Iterable= ()) -> None:
        self._iterator = iter(iterable)

    def expand(self, iterable: Iterable):
        self._iterator = chain(self._iterator, iter(iterable))

    def __next__(self):
        return next(self._iterator)
