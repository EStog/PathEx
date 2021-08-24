from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.nary_operators.shuffle import Shuffle

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
    mismatches = machine.mismatch(head1, head2)
    for m1, m2 in mismatches:
        yield from machine.branches(Concatenation(Shuffle(m1, m2), tail))
