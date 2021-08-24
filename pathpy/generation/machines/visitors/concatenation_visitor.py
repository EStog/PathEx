from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, Machine

__all__ = ['concatenation_visitor']


def concatenation_visitor(machine: Machine, exp: Concatenation) -> Branches:
    if exp.head is not None:
        if exp.tail.head is None:
            yield from machine.branches(exp.head)
            return

        for head, tail in machine.branches(exp.head):
            tail = exp.tail if tail is EMPTY_WORD \
                else Concatenation(tail, exp.tail)
            if head is EMPTY_WORD:
                yield from machine.branches(tail)
            else:
                yield head, tail
