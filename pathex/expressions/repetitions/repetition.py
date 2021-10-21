from __future__ import annotations

from dataclasses import dataclass
from math import inf

from pathex.expressions.expression import Expression

__all__ = ['Repetition']


@dataclass(frozen=True, repr=False, init=False)
class Repetition(Expression):
    """This class represents a repetition.
    """
    argument: object
    """The expression to be repeated"""
    lower_bound: int = 0
    """The minimum amount of repetitions to be produced"""
    upper_bound: int | float | ... = inf
    """The amount of repetitions to be produced.
    If it is math.inf, it is assumed to be infinite"""

    def __init__(self, argument: object,
                 lower_bound: int = 0,
                 upper_bound: int | float | ... = inf):

        if upper_bound is ...:
            upper_bound = inf

        assert isinstance(lower_bound, int) and lower_bound > -1, \
            'Lower bound must be possitive int or cero'
        assert isinstance(upper_bound, int) or upper_bound == inf and \
            upper_bound > -1, \
            'Upper bound must be possitive int (not cero) or math.inf'
        assert lower_bound <= upper_bound, \
            'Lower bound must be less or equal to upper bound'

        object.__setattr__(self, 'argument', argument)
        object.__setattr__(self, 'lower_bound', lower_bound)
        object.__setattr__(self, 'upper_bound', upper_bound)

    def __repr__(self): # pragma: no cover
        return f'{self.__class__.__name__}({self.argument!r}, {self.lower_bound!r}, {self.upper_bound!r})'
