from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Collection, Iterator, Protocol, TypeVar

from pathex.expressions.expression import Expression

__all__ = ['NAryOperator']

_T_co = TypeVar('_T_co', covariant=True)


class HashableCollection(Protocol[_T_co]):
    def __hash__(self) -> int: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[_T_co]: ...


@dataclass(frozen=True)
class NAryOperator(Expression):
    """Abstract base class for nary operators.

    An nary operator must have at least one argument. This is checked in debug mode.

    >>> from pathex import Union
    >>> try:
    ...    Union()
    ... except AssertionError:
    ...    pass # Right!
    ... else:
    ...    print('Wrong!')
    """
    arguments: Collection

    def __init__(self, *args) -> None:
        if len(args) == 1:
            args = args[0]
        object.__setattr__(self, 'arguments', tuple(args))
        assert len(self.arguments) > 0, 'arguments length should never be cero'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{tuple(self.arguments)}'

    @property
    def args_head(self):
        return next(iter(self.arguments))

    @cached_property
    def args_tail(self):
        it = iter(self.arguments)
        next(it)
        return tuple(it)

    # Must be implemented explicitly, to allow to be used by its children.
    def __eq__(self, o: object) -> bool:
        if isinstance(o, NAryOperator):
            return self.arguments == o.arguments
        else:
            return False
