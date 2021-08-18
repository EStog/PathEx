from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .expression import Expression

__all__ = ['Substitution']


@dataclass(frozen=True, repr=False)
class Substitution(Expression):
    """

    Example:

        >>> from pathpy import Concatenation as C, Union as U, EMPTY_WORD as e, WILDCARD as _

        >>> exp = C('abc')['a':'c', 'c':'a']
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'cba'}

        >>> exp = C('abc')['a':'xy', 'c':e]
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'xyb'}

        >>> exp = C(U('ax'), 'c')['a':'b', 'c':'y']
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'by', 'xy'}

        >>> exp = C('abca')['a':_]
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'_0bc_0'}

        >>> exp = C('abcacd')['c':_, 'a':'x'+_+'y']
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'x_0yb_1x_0y_1d'}

        >>> exp = C(U('xyz'), *'abc')['x':_, 'y':'w'+_, 'z':'t', 'b':C('r',_,'s')]
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'_0ar_1sc', 'w_0ar_1sc', 'tar_0sc'}
    """
    argument: object
    replacements: dict[object, object]

    def __init__(self, argument: object, replacements: Mapping[object, object]) -> None:
        object.__setattr__(self, 'argument', argument)
        object.__setattr__(self, 'replacements', dict(replacements))

    def __repr__(self):
        return f'{self.__class__.__name__}({self.argument!r}, {self.replacements!r})'

    def __str__(self):
        replacements = ''
        for key in self.replacements:
            replacements += f'{key!s}:{self.replacements[key]!s}, '
        return f'{self.argument!s}[{replacements[:-2]}]'

    def __hash__(self):
        return hash((self.argument, tuple(self.replacements.items())))
