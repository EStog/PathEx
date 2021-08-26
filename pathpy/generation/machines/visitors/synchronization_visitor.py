from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.nary_operators.shuffle import Shuffle

from ..machine import Branches, MachineWithMatchMismatch
from .decorators import matching_operator_visitor, nary_operator_visitor

__all__ = ['synchronization_visitor']


@nary_operator_visitor
@matching_operator_visitor
def synchronization_visitor(machine: MachineWithMatchMismatch, head1, head2, tail) -> Branches:
    # `a @ b = a`                     if `a == b`
    for match in machine.match(head1, head2):
        yield match, tail
    # `a @ b = a // b`                if `a != b`
    for m1, m2 in machine.mismatch(head1, head2):
        yield from machine.branches(Concatenation(Shuffle(m1, m2), tail))
