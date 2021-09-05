from pathex.expressions.nary_operators.shuffle import Shuffle
from pathex.expressions.nary_operators.union import Union
from pathex.expressions.repetitions.shuffle_repetition import ShuffleRepetition
from pathex.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, Machine
from .misc import NOT_EMPTY_WORD_MESSAGE

__all__ = ['shuffle_repetition_visitor']


def shuffle_repetition_visitor(machine: Machine, exp: ShuffleRepetition) -> Branches:
    assert exp.argument is not EMPTY_WORD, NOT_EMPTY_WORD_MESSAGE

    # a//1 = a
    if exp.lower_bound == exp.upper_bound == 1:
        yield EMPTY_WORD, exp.argument

    # a%n = empty | a%[1,n]
    elif exp.lower_bound == 0:
        yield (EMPTY_WORD,
               Union(
                   EMPTY_WORD,
                   ShuffleRepetition(
                       exp.argument,
                       1, exp.upper_bound)))
    else:
        for head, tail in machine.branches(exp.argument):

            # (aB)%[n,m] = a*[n,m] if `B` is empty string
            if tail is EMPTY_WORD:
                yield EMPTY_WORD, exp.as_concatenation_repetition()

            # = a + (B // aB%[n-1,m-1] ) where n > 0
            else:
                yield (head,
                       Shuffle.flattened(
                           tail,
                           ShuffleRepetition(
                               exp.argument,
                               exp.lower_bound-1,
                               exp.upper_bound-1)))
