
from pathex.expressions.nary_operators.concatenation import Concatenation
from pathex.expressions.repetitions.concatenation_repetition import \
    ConcatenationRepetition
from pathex.expressions.terms.empty_word import EMPTY_WORD
from pathex.machines.decomposers.visitors.decorators import repetition_visitor

from pathex.machines.decomposers.decomposer import Branches, Decomposer

__all__ = ['concatenation_repetition_visitor']


@repetition_visitor
def concatenation_repetition_visitor(machine: Decomposer, exp: ConcatenationRepetition) -> Branches:
    # a*[n,m] = a + a*[n-1,m-1] where n > 0
    yield EMPTY_WORD, Concatenation(exp.argument,
                                     ConcatenationRepetition(
                                         exp.argument, exp.lower_bound-1, exp.upper_bound-1))
