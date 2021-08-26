from pathpy.expressions.terms.empty_word import EMPTY_WORD
from pathpy.expressions.terms.letter import Letter

from ..machine import Branches, Machine


def letter_visitor(machine: Machine, exp: Letter) -> Branches:
    yield exp.value, EMPTY_WORD
