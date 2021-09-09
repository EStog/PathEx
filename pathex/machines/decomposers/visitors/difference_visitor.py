from collections import deque
from pathex.machines.decomposers.visitors.decorators import nary_operator_visitor
from pathex.expressions.nary_operators.difference import Difference
from pathex.expressions.terms.empty_word import EMPTY_WORD

from ..decomposer import Branches, DecomposerMatchMismatch

__all__ = ['difference_visitor']

@nary_operator_visitor
def difference_visitor(machine: DecomposerMatchMismatch, exp: Difference) -> Branches:
    for head1, tail1 in machine._transform(exp.args_head):
        if head1 is EMPTY_WORD and tail1 is not EMPTY_WORD:
            yield EMPTY_WORD, exp.__class__(tail1, *exp.args_tail)
        else:
            matches = set()
            mismatches = {}
            alts = deque([Difference(exp.args_tail)])
            while alts:
                other = alts.popleft()
                for head2, tail2 in machine._transform(other):
                    if head2 is EMPTY_WORD and tail2 is not EMPTY_WORD:
                        alts.append(tail2)
                    else:
                        tail = EMPTY_WORD if tail1 is tail2 is EMPTY_WORD \
                            else Difference(tail1, tail2)
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
