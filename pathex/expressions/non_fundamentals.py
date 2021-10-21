from __future__ import annotations

from pathex.expressions.nary_operators.union import Union
from pathex.expressions.terms.empty_word import EMPTY_WORD

__all__ = ['optional']


def optional(argument: object):
    return Union((EMPTY_WORD, argument))
