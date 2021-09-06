from pathex.expressions.nary_operators.union import Union
from pathex.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, Machine

__all__ = ['union_visitor']


def union_visitor(machine: Machine, exp: Union) -> Branches:
    for e in exp:
        yield EMPTY_WORD, e
