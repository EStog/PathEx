from pathex.expressions.terms.empty_word import EMPTY_WORD
from pathex.machines.decomposers.decomposer import Branches, Decomposer

__all__ = ['object_visitor']


def object_visitor(machine: Decomposer, exp: object) -> Branches:
    yield exp, EMPTY_WORD
