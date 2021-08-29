from pathex.expressions.nary_operators.difference import Difference
from pathex.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, MachineWithMatchMismatch
from .decorators import nary_operator_visitor

__all__ = ['difference_visitor']


@nary_operator_visitor
def difference_visitor(machine: MachineWithMatchMismatch, exp: Difference) -> Branches:
    for head1, tail1 in machine.branches(exp.head):
        matches = set()
        mismatches = {}
        for head2, tail2 in machine.branches(exp.tail):

            tail = EMPTY_WORD if tail1 is tail2 is EMPTY_WORD \
                else exp.__class__(tail1, tail2)

            for match in machine.match(head1, head2):
                matches.add(match)
                if match in mismatches:
                    del mismatches[match]
                if tail is not EMPTY_WORD:
                    yield match, tail

            for m, h in machine.mismatch(head1, head2):
                if h is not head2:
                    break
                if m not in matches:
                    mismatches[m] = tail
        for m in mismatches:
            yield m, mismatches[m]
