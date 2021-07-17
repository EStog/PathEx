from __future__ import annotations
from typing import cast

from pathpy.adts.containers.head_tail_iterable import HeadTailIterable

from ..expression import Expression


class NAryOperator(HeadTailIterable[Expression], Expression):

    def __new__(cls, *args):
        if len(args) == 1:
            args = args[0]
        return cast(cls, HeadTailIterable.__new__(cls, args))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{tuple(self)}'


__all__ = ['NAryOperator']
