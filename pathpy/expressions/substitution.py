from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .expression import Expression


@dataclass(frozen=True, repr=False)
class Substitution(Expression):
    """Returns a function `Substitution -> Iterable[Concatenation]`
    to visit a `Substitution` expression.

    `Substitution` is semantically equivalent to the replacement,
    by a given object, of a letter of the strings in a given language.

    In the notation `A[D]`, `A` is an expression and `D` is a dictionary
    that contains the replacements. Roughly speaking, it means that the
    result of A[D] is a set of strings, each one of them taken from `A`
    but with each occurrence of `key in D.keys()` replaced by `D[key]`.

        (aA)[D,a:_] = (aA)[D,a:v]
            where type(v)=NamedWildcard and type(a)=Letter
                and `v` not in `A`

        (aA)[D,a:_R] = (aA)[D,a:vR]
            where type(v)=NamedWildcard and type(a)=Letter
                and `v` not in `A`

        a[D,a:r]     = r
        (aA)[D,a:r]  = r + A[D,a:r]

        a[D,a:rR]    = r + R
        (aA)[D,a:rR] = r + R + A[D,a:rR]
            where `c` not in `A`

        So the following case should never occur:
            A[x:a] + B[x:b]
                where type(x)=NamedWildcard and
                type(a)=type(b)=Letter and a != b

    Example:
        >>> from pathpy import Concatenation as C, Union as U, EMPTY_STRING as e, WILDCARD as _

        >>> exp = C('abc')[{'a':'c', 'c':'a'}]
        >>> assert exp.as_(set) == {'cba'}

        >>> exp = C('abc')['a':'xy', 'c':e]
        >>> assert exp.as_(set) == {'xyb'}

        >>> exp = C(U('ax'), 'c')['a':'b', 'c':'y']
        >>> assert exp.as_(set) == {'by', 'xy'}

        >>> from pathpy.generators.word_generator import WordGenerator
        >>> from pathpy.generators._expressions._named_wildcard import NamedWildcard
        >>> def word_reifier(word):
        ...     s = ''
        ...     for x in word.reification(complete=True):
        ...         if isinstance(x, NamedWildcard):
        ...             s += f'_{x.name}'
        ...         else:
        ...             s += str(x)
        ...     return s

        >>> exp = C('abca')['a':_]
        >>> assert set(exp.reification(word_reifier=word_reifier)) == {'_0bc_0'}

        >>> exp = C('abcacd')['c':_, 'a':'x'+_+'y']
        >>> assert set(exp.reification(word_reifier=word_reifier)) == {'x_0yb_1x_0y_1d'}

        >>> exp = C(U('xyz'), *'abc')['x':_, 'y':'w'+_, 'z':'t', 'b':C('r',_,'s')]
        >>> assert set(exp.reification(word_reifier=word_reifier)) == {'_0ar_1sc', 'w_0ar_1sc', 'tar_0sc'}
    """
    argument: object
    replacements: dict[object, object]

    def __init__(self, argument: object, replacements: Mapping[object,object]) -> None:
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


__all__ = ['Substitution']
