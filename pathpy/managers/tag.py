from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Iterator, Union

from pathpy.expressions.nary_operators.concatenation import Concatenation

__all__ = ['Tag']


@dataclass(frozen=True, init=False, eq=False)
class Tag(Concatenation):
    """A Tag identifies a region, where traces needs to be managed.

    A Tag is just a concatenation of two Labels objects, identifying the beginning and the end of the region.
    """

    enter: Label
    exit: Label

    def __init__(self, name=None):
        if name is None:
            name = id(self)
        else:
            object.__setattr__(self, 'name', name)

        enter = Enter(name)
        exit = Exit(name)
        super().__init__(enter, exit)

        object.__setattr__(self, 'enter', enter)
        object.__setattr__(self, 'exit', exit)
        object.__setattr__(self, 'head', enter)

    @cached_property
    def tail(self):
        return Concatenation([self.exit])

    def __repr__(self) -> str:
        if hasattr(self, 'name'):
            return f'{self.__class__.__name__}({self.name})'
        else:
            return f'{self.__class__.__name__}({id(self)})'

    def __hash__(self) -> int:
        return id(hash)

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


@dataclass(frozen=True)
class Label:
    """This class represents an object that is part of a Tag.
    Label objects are used to identify the beginning and the end of a region
    """
    name: Union[int, str]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name})'

    def __hash__(self) -> int:
        return id(self)


class Enter(Label):
    pass


class Exit(Label):
    pass
