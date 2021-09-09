from pathex.machines.decomposers.visitors.decorators import nary_operator_visitor
from pathex.expressions.nary_operators.union import Union
from pathex.expressions.terms.empty_word import EMPTY_WORD

from ..decomposer import Branches, Decomposer

__all__ = ['union_visitor']

@nary_operator_visitor
def union_visitor(machine: Decomposer, exp: Union) -> Branches:
    for e in exp.arguments:
        yield EMPTY_WORD, e
