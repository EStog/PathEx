from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.nary_operators.synchronization import Synchronization
from pathpy.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, MachineWithMatchUnmatch
from .decorators import nary_operator_visitor

__all__ = ['synchronization_visitor']

@nary_operator_visitor
def synchronization_visitor(machine: MachineWithMatchUnmatch, exp: Synchronization) -> Branches:
    for head1, tail1 in machine.branches(exp.head):
        for head2, tail2 in machine.branches(exp.tail):
            # `aA @ bB = (a @ b) + (A @ B)`
            tail = EMPTY_WORD if tail1 is tail2 is EMPTY_WORD \
                else Synchronization(tail1, tail2)
            # `a @ b = a`                     if `a == b`
            match = machine.match(head1, head2)
            if match:
                yield head1, tail
            # `a @ b = a // b`                if `a != b`
            matchs = machine.unmatch(head1, head2)
            for match in matchs:
                if match:
                    yield from machine.branches(Concatenation(match, tail))
