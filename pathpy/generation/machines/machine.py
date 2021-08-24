from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import singledispatchmethod
from typing import Iterable, Iterator

__all__ = ['Machine']

Branches = Iterator[tuple[object, object]]


@dataclass(frozen=True)
class Machine(ABC):

    def __init_subclass__(cls):
        cls._populate_visitor()

    @singledispatchmethod
    @abstractmethod
    def branches(self, exp: object) -> Branches: ...

    @classmethod
    @abstractmethod
    def _populate_visitor(cls): ...


class MachineWithMatch(Machine):
    @abstractmethod
    def match(self, value1: object, value2: object) -> object: ...


class MachineWithUnmatch(Machine):
    @abstractmethod
    def mismatch(self, value1: object, value2: object) -> Iterable[tuple[object, object]]: ...


class MachineWithMatchUnmatch(MachineWithMatch, MachineWithUnmatch):
    pass
