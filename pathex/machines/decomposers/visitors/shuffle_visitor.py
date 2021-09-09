from collections import deque
from pathex.machines.decomposers.visitors.decorators import nary_operator_visitor

from pathex.expressions.nary_operators.shuffle import Shuffle
from pathex.expressions.terms.empty_word import EMPTY_WORD

from ..decomposer import Branches, Decomposer

__all__ = ['shuffle_visitor']

@nary_operator_visitor
def shuffle_visitor(machine: Decomposer, exp: Shuffle) -> Branches:
    front = deque()
    back = deque(exp.arguments)
    while back:
        e = back.popleft()
        for head, tail in machine._transform(e):
            tail = Shuffle(front + back) if tail is EMPTY_WORD else \
                Shuffle(tail, *(front + back))
            yield head, tail
        front.append(e)
