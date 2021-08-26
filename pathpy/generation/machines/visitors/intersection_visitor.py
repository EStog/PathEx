from __future__ import annotations

from pathpy.expressions.nary_operators.intersection import Intersection
from pathpy.expressions.terms.empty_word import EmptyWord
from pathpy.expressions.nary_operators.nary_operator import NAryOperator

from ..machine import Branches, MachineWithMatch
from .decorators import matching_operator_visitor, nary_operator_visitor

__all__ = ['intersection_visitor']


@nary_operator_visitor
@matching_operator_visitor
def intersection_visitor(machine: MachineWithMatch, head1: object, head2: object, tail: object) -> Branches:
    # `a & b = a`                 if `a == b`
    for match in machine.match(head1, head2):
        yield match, tail
    # `a & b = {}`                if `a != b`
