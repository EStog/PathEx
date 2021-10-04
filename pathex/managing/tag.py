from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterator, Optional

from pathex.expressions.nary_operators.concatenation import Concatenation

__all__ = ['Tag']


@dataclass(frozen=True, init=False, eq=False)
class Tag(Concatenation):
    """A Tag identifies a region, where traces needs to be managed.

    A Tag is just a concatenation of two Labels objects, identifying the beginning and the end of the region.

    They compare as concatenations:

    .. testsetup::

       from pathex import Tag

    >>> a = Tag('a')
    >>> from pathex import Concatenation
    >>> b = Concatenation(a.enter, a.exit)
    >>> assert a == b
    >>> assert hash(a) == hash(b)

    However the representation is different to ease debugging:

    >>> repr(a)
    "Tag('a')"
    >>> repr(b)
    "Concatenation('a.enter', 'a.exit')"
    """

    enter: str
    exit: str
    name: Hashable

    def __init__(self, name: Optional[Hashable] = None):
        if name is None:
            name = id(self)

        object.__setattr__(self, 'name', name)

        enter = f'{name}.enter'
        exit = f'{name}.exit'

        super().__init__((enter, exit))

        object.__setattr__(self, 'enter', enter)
        object.__setattr__(self, 'exit', exit)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r})'

    @classmethod
    def anonym(cls, n: int) -> Iterator[Tag]:
        """Factory method that gives `n` tags.

        .. testsetup::

           from pathex import Tag

        >>> a, b = Tag.anonym(2)
        >>> assert a.name == id(a)
        >>> assert b.name == id(b)

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

        .. testsetup::

           from pathex import Tag

        >>> a, b = Tag.named('a', 'b')
        >>> assert a.name == 'a'
        >>> assert b.enter == 'b.enter'
        >>> assert b.exit == 'b.exit'

        Args:
            names (tuple[object]): The names for the constructed tags

        Returns:
            Iterator[Tag]: an iterator that gives tags with the given names.
        """
        return (cls(name) for name in names)
