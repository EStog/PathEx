from __future__ import annotations

from pathpy.adts.containers.head_tail_iterable import HeadTailIterable

from ..expression import Expression


class NAryOperator(HeadTailIterable, Expression):

    head: Expression
    tail: Expression

    def __new__(cls, *args: object):
        return HeadTailIterable.__new__(cls, args)

    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        HeadTailIterable.__init__(self, args)
        if not self.has_head:
            raise TypeError(
                'Iterable must have at least two elements. Cero found')
        if not self.has_tail:
            raise TypeError(
                'Iterable must have at least two elements. Only one found')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{tuple(self)}'


__all__ = ['NAryOperator']
