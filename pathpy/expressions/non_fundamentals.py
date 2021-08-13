from __future__ import annotations

from collections.abc import Iterable
from functools import partial
from typing import Callable, Mapping

from pathpy.generators.symbols_table import SymbolsTable

from .nary_operators.intersection import Intersection
from .nary_operators.nary_operator import NAryOperator
from .nary_operators.union import Union
from .negation import Negation
from .substitution import Substitution
from .terms.letters_unions.letters_possitive_union import LettersPossitiveUnion
from .terms.empty_string import EMPTY_STRING

__all__ = ['difference', 'symmetric_difference', 'multiplication']


def letter(obj):
    return LettersPossitiveUnion({obj})


def difference(*args: object):
    it = iter(args)
    try:
        x = next(it)
    except StopIteration:
        return Intersection()
    else:
        return Intersection(x, map(Negation, it))


def symmetric_difference(x: object, y: object):
    return difference(Union(x, y), Intersection(x, y))


def multiplication(argument: object, operator: Callable[..., NAryOperator],
                   replacements: Iterable[Mapping[object, object]]):
    if not isinstance(replacements, Iterable):
        raise TypeError('Replacements must be iterable')
    try:
        return operator(map(partial(Substitution, argument=argument), replacements))
    except TypeError:
        raise TypeError(
            'Multiplication must take more than one replacement. For only one replacement use Substitution instead')


# def left_multiplication(argument: object, operator: Callable[[Iterable], NAryOperator],
#                         replacements: Iterable[Mapping[object, object]]):
#     pass

def conditional(predicate: Callable[[], bool], consequent: object=EMPTY_STRING, alternative: object=Union()) -> Callable[[SymbolsTable, object], tuple[object, SymbolsTable, object]]:
    def func(table: SymbolsTable, extra: object) -> tuple[object, SymbolsTable, object]:
        if predicate():
            return consequent, table, extra
        else:
            return alternative, table, extra

    return func
