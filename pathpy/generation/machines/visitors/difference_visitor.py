from pathpy.expressions.nary_operators.difference import Difference
from pathpy.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, MachineWithMatchMismatch
from .decorators import nary_operator_visitor

__all__ = ['difference_visitor']


@nary_operator_visitor
def difference_visitor(machine: MachineWithMatchMismatch, exp: Difference) -> Branches:
    for head1, tail1 in machine.branches(exp.head):
        # this variables are just to support the case of the presence of wildcards. In the simple case without wildcards, this is fairly harmless.
        matches = set()
        mismatches = {}
        for head2, tail2 in machine.branches(exp.tail):
            # `aA op bB = (a match b) + (A match B)`
            tail = EMPTY_WORD if tail1 is tail2 is EMPTY_WORD \
                else exp.__class__(tail1, tail2)
            # `a @ b = a`                     if `a == b`
            match = machine.match(head1, head2)
            if match:
                matches.add(match)
                if match in mismatches:
                    del mismatches[match]
                if tail is not EMPTY_WORD:
                    yield match, tail
            # `a @ b = a // b`                if `a != b`
            if mss := machine.mismatch(head1, head2):
                if (mismatch := mss[0][0]) not in matches:
                    mismatches[mismatch] = tail
        for m in mismatches:
            yield m, mismatches[m]
