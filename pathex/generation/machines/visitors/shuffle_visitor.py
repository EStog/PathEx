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
            if head is not EMPTY_WORD:
                rest = Shuffle(front + back)
                tail = rest if tail is EMPTY_WORD else Shuffle(tail, rest)
                yield head, tail
        front.append(e)
