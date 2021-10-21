from abc import abstractmethod
from functools import singledispatchmethod
from typing import Iterable, Iterator, Sequence

from pathex.machines.machine import Machine

__all__ = ['Branches', 'Decomposer', 'DecomposerMatch',
           'DecomposerMismatch', 'DecomposerMatchMismatch']

Branches = Iterator[tuple[object, object]]


class Decomposer(Machine):

    def __init_subclass__(cls):
        cls._populate_transformer()

    @classmethod
    def _populate_transformer(cls): ...

    def __init__(self, simplifier=None):
        if simplifier is None:
            from pathex.machines.simplifier import Simplifier
            simplifier = Simplifier()
        self._simplifier = simplifier

    def transform(self, exp: object) -> Branches:
        for head, tail in self._transform(self._simplifier.transform(exp)):
            yield head, self._simplifier.transform(tail)

    @singledispatchmethod
    @abstractmethod
    def _transform(self, exp: object) -> Branches: ...


Matches = Iterable[object]


class DecomposerMatch(Decomposer):
    @abstractmethod
    def match(self, value1: object, value2: object) -> Matches: ...


class DecomposerMismatch(Decomposer):
    @abstractmethod
    def mismatch(self, value1: object,
                 value2: object) -> Sequence[tuple[object, object]]: ...


class DecomposerMatchMismatch(DecomposerMatch, DecomposerMismatch):
    pass
