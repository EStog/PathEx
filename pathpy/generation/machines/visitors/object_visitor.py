from pathpy.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, Machine

__all__ = ['object_visitor']


def object_visitor(machine: Machine, exp: object) -> Branches:
    yield exp, EMPTY_WORD
