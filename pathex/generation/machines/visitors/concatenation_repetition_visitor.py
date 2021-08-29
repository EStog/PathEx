
from pathex.expressions.nary_operators.concatenation import Concatenation
from pathex.expressions.nary_operators.union import Union
from pathex.expressions.repetitions.concatenation_repetition import \
    ConcatenationRepetition
from pathex.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, Machine
from .misc import NOT_EMPTY_WORD_MESSAGE

__all__ = ['concatenation_repetition_visitor']


def concatenation_repetition_visitor(machine: Machine, exp: ConcatenationRepetition) -> Branches:
    assert exp.argument is not EMPTY_WORD, NOT_EMPTY_WORD_MESSAGE

    # a+1 = a
    if exp.lower_bound == exp.upper_bound == 1:
        return machine.branches(exp.argument)

    # a*n = empty | a*[1,n]
    elif exp.lower_bound == 0:
        return machine.branches(
            Union(
                EMPTY_WORD,
                ConcatenationRepetition(
                    exp.argument,
                    1, exp.upper_bound)))

    # a*[n,m] = a + a*[n-1,m-1] where n > 0
    else:
        return machine.branches(
            Concatenation.new(
                exp.argument,
                ConcatenationRepetition(
                    exp.argument,
                    exp.lower_bound-1,
                    exp.upper_bound-1)))
