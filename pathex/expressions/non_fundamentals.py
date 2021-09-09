from __future__ import annotations

from .nary_operators.union import Union
from .terms.empty_word import EMPTY_WORD

__all__ = ['optional']


def optional(argument: object):
    return Union((EMPTY_WORD, argument))
