from pathex.expressions.nary_operators.concatenation import Concatenation
from pathex.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, Machine
from .decorators import nary_operator_visitor

__all__ = ['concatenation_visitor']


@nary_operator_visitor
def concatenation_visitor(machine: Machine, exp: Concatenation) -> Branches:
    for head, tail in machine.branches(exp.head):
        tail = exp.tail if tail is EMPTY_WORD \
            else Concatenation.flattened(tail, exp.tail)
        yield head, tail
