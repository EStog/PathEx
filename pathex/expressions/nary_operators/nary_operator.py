from __future__ import annotations
from collections import deque

from dataclasses import dataclass
from functools import cached_property
from typing import TypeVar

from pathex.adts.containers.head_tail_iterable import HeadTailIterable

from ..expression import Expression

__all__ = ['NAryOperator']
_T = TypeVar('_T', bound='NAryOperator')

@dataclass(frozen=True, repr=False)
class NAryOperator(Expression):

    arguments: HeadTailIterable[object]
    head: object

    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        object.__setattr__(self, 'arguments', HeadTailIterable(args))
        object.__setattr__(self, 'head', self.arguments.head)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{tuple(self.arguments)}'

    @cached_property
    def tail(self: _T) -> _T:
        return self.__class__(self.arguments.tail)

    def __iter__(self):
        return iter(self.arguments)
