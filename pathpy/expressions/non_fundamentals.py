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
        def f(arg):
            def p(r):
                return Substitution(argument=arg, replacements=r)
            return p
        return operator(map(f(argument), replacements))
    except TypeError as e:
        print(e)
        raise TypeError(
            'Multiplication must take more than one replacement. For only one replacement use Substitution instead')


# def left_multiplication(argument: object, operator: Callable[[Iterable], NAryOperator],
#                         replacements: Iterable[Mapping[object, object]]):
#     pass

def conditional(*branches: tuple[Callable[[], bool], object], otherwise: object=Union()) -> Callable[[SymbolsTable, object], tuple[object, SymbolsTable, object]]:
    def func(table: SymbolsTable, extra: object) -> tuple[object, SymbolsTable, object]:
        for predicate, consequence in branches:
            if predicate():
                return consequence, table, extra
        return otherwise, table, extra

    return func
