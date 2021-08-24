from pathpy.expressions.nary_operators.shuffle import Shuffle
from pathpy.expressions.nary_operators.union import Union
from pathpy.expressions.repetitions.shuffle_repetition import ShuffleRepetition
from pathpy.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, Machine
from .misc import NOT_EMPTY_WORD_MESSAGE

__all__ = ['shuffle_repetition_visitor']


def shuffle_repetition_visitor(machine: Machine, input: ShuffleRepetition) -> Branches:
    assert input.argument is not EMPTY_WORD, NOT_EMPTY_WORD_MESSAGE

    # a//1 = a
    if input.lower_bound == input.upper_bound == 1:
        yield from machine.branches(input.argument)

    # a%n = empty | a%[1,n]
    elif input.lower_bound == 0:
        yield from machine.branches(
            Union(
                EMPTY_WORD,
                ShuffleRepetition(
                    input.argument,
                    1, input.upper_bound)))
    else:
        for head, tail in machine.branches(input.argument):

            # (aB)%[n,m] = a*[n,m] if `B` is empty string
            if tail is EMPTY_WORD:
                yield from machine.branches(
                    input.as_concatenation_repetition())

            # = a + (B // aB%[n-1,m-1] ) where n > 0
            else:
                yield (head,
                       Shuffle(
                           tail,
                           ShuffleRepetition(
                               input.argument,
                               input.lower_bound-1,
                               input.upper_bound-1)))
