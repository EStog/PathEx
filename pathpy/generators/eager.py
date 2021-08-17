from __future__ import annotations

from copy import copy

from pathpy.adts.collection_wrapper import CollectionWrapper
from pathpy.expressions.expression import Expression
from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.terms.empty_word import EMPTY_WORD

from .alternatives_generator import AlternativesGenerator
from .defaults import (ALTERNATIVES_COLLECTION_TYPE, ONLY_COMPLETE_WORDS,
                       WORD_TYPE)
from .symbols_table import SymbolsTable

__all__ = ['get_language']


def _get_alternatives(
        prefix_type: type[CollectionWrapper],
        expression: Expression, table: SymbolsTable, extra: object,
        alternatives_collection_type: type[CollectionWrapper],
        only_complete_words: bool):

    alternatives = alternatives_collection_type()
    alternatives.put((prefix_type(), expression, table, extra))

    while True:
        try:
            prefix, tail, table, extra = alternatives.pop()
        except alternatives.PopException:
            break
        else:
            alt = AlternativesGenerator(tail, table, extra)
            tail = None
            for head, tail, table, extra in alt:
                prefix_copy = copy(prefix)
                prefix_copy.put(head)
                if tail is EMPTY_WORD:
                    yield prefix_copy, table, extra
                else:
                    alternatives.put((prefix_copy, tail, table, extra))
            if tail is None and not only_complete_words:
                yield prefix, table, extra


def get_language(expression: Expression, table: SymbolsTable, extra: object,
                 word_type: type[CollectionWrapper] = WORD_TYPE,
                 alternatives_collection_type: type[CollectionWrapper] = ALTERNATIVES_COLLECTION_TYPE,
                 only_complete_words: bool = ONLY_COMPLETE_WORDS):

    for prefix, table, extra in _get_alternatives(word_type, expression, table, extra,
                                                  alternatives_collection_type,
                                                  only_complete_words):
        if not prefix:
            prefix.put(EMPTY_WORD)
            yield prefix
        else:
            for prefix, _, _ in _get_alternatives(word_type, Concatenation(prefix), table, extra,
                                                  alternatives_collection_type,
                                                  only_complete_words):
                yield prefix
