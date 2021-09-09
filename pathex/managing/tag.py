from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from pathex.expressions.nary_operators.concatenation import Concatenation

__all__ = ['Tag']


@dataclass(frozen=True, init=False, eq=False)
class Tag(Concatenation):
    """A Tag identifies a region, where traces needs to be managed.

    A Tag is just a concatenation of two Labels objects, identifying the beginning and the end of the region.
    """

    enter: str
    exit: str

    def __init__(self, name=None):
        if name is None:
            name = id(self)
        else:
            object.__setattr__(self, '_name', name)

        enter = f'{name}.enter'
        exit =  f'{name}.exit'

        super().__init__((enter, exit))

        object.__setattr__(self, 'enter', enter)
        object.__setattr__(self, 'exit', exit)

    @property
    def name(self):
        if hasattr(self, '_name'):
            return self._name
        else:
            return id(self)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r})'

    def __hash__(self) -> int:
        return id(self)

    @classmethod
    def anonym(cls, n: int) -> Iterator[Tag]:
        """Factory method that gives `n` tags.

        The names of the tags are the same as its object ids.

        Args:
            n (int): The amount of tags to be constructed

        Returns:
            Iterator[Tag]: an iterator that gives `n` anonymous tags.
        """
        return (cls() for _ in range(n))

    @classmethod
    def named(cls, *names: object) -> Iterator[Tag]:
        """Factory method that gives named tags.

        Args:
            names (tuple[object]): The names for the constructed tags

        Returns:
            Iterator[Tag]: an iterator that gives tags with the given names.
        """
        return (cls(name) for name in names)
