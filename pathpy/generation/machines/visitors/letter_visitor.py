from pathpy.expressions.terms.empty_word import EMPTY_WORD
from pathpy.expressions.terms.letter import Letter

from ..machine import Branches


def letter_visitor(self, exp: Letter) -> Branches:
    yield exp.value, EMPTY_WORD
