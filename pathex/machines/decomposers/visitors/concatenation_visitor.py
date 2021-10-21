from pathex.machines.decomposers.visitors.decorators import nary_operator_visitor
from pathex.expressions.nary_operators.concatenation import Concatenation
from pathex.expressions.terms.empty_word import EMPTY_WORD

from pathex.machines.decomposers.decomposer import Branches, Decomposer

__all__ = ['concatenation_visitor']

@nary_operator_visitor
def concatenation_visitor(decomposer: Decomposer, exp: Concatenation) -> Branches:
    for head, tail in decomposer._transform(exp.args_head):
        tail = Concatenation(exp.args_tail) if tail is EMPTY_WORD \
            else Concatenation(tail, *exp.args_tail)
        yield head, tail
