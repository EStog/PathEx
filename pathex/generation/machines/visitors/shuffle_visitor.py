from collections import deque

from pathex.expressions.nary_operators.shuffle import Shuffle
from pathex.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, Machine
from .decorators import nary_operator_visitor

__all__ = ['shuffle_visitor']


@nary_operator_visitor
def shuffle_visitor(machine: Machine, exp: Shuffle) -> Branches:
    front = deque()
    back = deque(exp.arguments)
    while back:
        e = back.popleft()
        for head, tail in machine.branches(e):
            tail = Shuffle.flattened(front + back) if tail is EMPTY_WORD else \
                Shuffle.flattened([tail, *(front + back)])
            yield head, tail
        front.append(e)
