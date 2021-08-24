from pathpy.expressions.nary_operators.shuffle import Shuffle
from pathpy.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, Machine

__all__ = ['shuffle_visitor']


def shuffle_visitor(machine: Machine, input: Shuffle) -> Branches:
    if input.head is not None:
        if input.tail.head is None:
            yield from machine.branches(input.head)
            return

        def shuffle(a, b):
            for head, tail in machine.branches(a):
                # aA // B = a + (A // B) | ...
                if tail is not EMPTY_WORD:
                    yield head, Shuffle(tail, b)
                else:
                    # a // B = a + B | ...
                    yield head, b

        yield from shuffle(input.head, input.tail)
        yield from shuffle(input.tail, input.head)
