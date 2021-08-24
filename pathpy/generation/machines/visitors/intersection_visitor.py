from pathpy.expressions.nary_operators.intersection import Intersection
from pathpy.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, MachineWithMatch

__all__ = ['intersection_visitor']


def intersection_visitor(machine: MachineWithMatch, input: Intersection) -> Branches:
    if input.head is not None:
        if input.tail.head is None:
            yield from machine.branches(input.head)
            return

        for head1, tail1 in machine.branches(input.head):
            for head2, tail2 in machine.branches(input.tail):
                # `aA & bB = (a & b) + (A & B)`
                tail = EMPTY_WORD if tail1 is tail2 is EMPTY_WORD \
                    else Intersection(tail1, tail2)
                # `a & b = a`                 if `a == b`
                match = machine.match(head1, head2)
                if match:
                    yield match, tail
                # `a & b = {}`                if `a != b`
