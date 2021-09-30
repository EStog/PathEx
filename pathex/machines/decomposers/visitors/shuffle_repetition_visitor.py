from pathex.expressions.nary_operators.shuffle import Shuffle
from pathex.expressions.repetitions.shuffle_repetition import ShuffleRepetition
from pathex.expressions.terms.empty_word import EMPTY_WORD
from pathex.machines.decomposers.visitors.decorators import repetition_visitor

from ..decomposer import Branches, Decomposer

__all__ = ['shuffle_repetition_visitor']

@repetition_visitor
def shuffle_repetition_visitor(decomposer: Decomposer, exp: ShuffleRepetition) -> Branches:
    for head, tail in decomposer._transform(exp.argument):

        # (aB)%[n,m] = a*[n,m] if `B` is empty string
        if tail is EMPTY_WORD:
            yield head, ShuffleRepetition(exp.argument, exp.lower_bound-1, exp.upper_bound-1)

        # = a + (B // aB%[n-1,m-1] ) where n > 0
        else:
            yield head, Shuffle(tail,
                                 ShuffleRepetition(
                                     exp.argument, exp.lower_bound-1, exp.upper_bound-1))
