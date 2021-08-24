from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.nary_operators.synchronization import Synchronization
from pathpy.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, MachineWithMatchUnmatch
from .decorators import matching_operator_visitor, nary_operator_visitor

__all__ = ['synchronization_visitor']

@nary_operator_visitor
@matching_operator_visitor
def synchronization_visitor(machine: MachineWithMatchUnmatch, head1, head2, tail) -> Branches:
    # `a @ b = a`                     if `a == b`
    match = machine.match(head1, head2)
    if match:
        yield head1, tail
    # `a @ b = a // b`                if `a != b`
    matchs = machine.unmatch(head1, head2)
    for match in matchs:
        if match:
            yield from machine.branches(Concatenation(match, tail))
