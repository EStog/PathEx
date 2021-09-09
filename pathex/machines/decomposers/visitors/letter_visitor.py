from pathex.expressions.terms.empty_word import EMPTY_WORD
from pathex.expressions.terms.letter import Letter

from ..decomposer import Branches, Decomposer


def letter_visitor(machine: Decomposer, exp: Letter) -> Branches:
    yield exp.value, EMPTY_WORD
