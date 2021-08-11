from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from pathpy.adts.containers.head_tail_iterable import HeadTailIterable

from ..expression import Expression

__all__ = ['NAryOperator']


@dataclass(frozen=True, init=False, repr=False)
class NAryOperator(Expression):

    arguments: HeadTailIterable[Expression]
    head: object

    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        object.__setattr__(self, 'arguments', HeadTailIterable(args))
        object.__setattr__(self, 'head', self.arguments.head)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{tuple(self.arguments)}'

    @cached_property
    def tail(self):
        return self.__class__(self.arguments.tail)

    def __iter__(self):
        return iter(self.arguments)

    @classmethod
    def new(cls, exp1, exp2):
        exp1_is_cls = isinstance(exp1, cls)
        exp2_is_cls = isinstance(exp2, cls)
        if exp1_is_cls and exp2_is_cls:
            return cls(exp1.arguments+exp2.arguments)
        elif exp1_is_cls:
            return cls(exp1.arguments.appended(exp2))
        elif exp2_is_cls:
            return cls(exp2.arguments.appended_left(exp1))
        else:
            return cls(exp1, exp2)
