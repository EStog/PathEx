from __future__ import annotations

from copy import copy

from pathpy.adts.collection_wrapper import CollectionWrapper
from pathpy.expressions.expression import Expression
from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.terms.empty_string import EMPTY_STRING

from .alternatives_generator import AlternativesGenerator
from .defaults import (ALTERNATIVES_COLLECTION_TYPE, ONLY_COMPLETE_WORDS,
                       WORD_TYPE)
from .symbols_table import SymbolsTable

__all__ = ['get_language']


def _get_alternatives(
        prefix_type: type[CollectionWrapper],
        expression: Expression, table: SymbolsTable,
        alternatives_collection_type: type[CollectionWrapper],
        only_complete_words: bool):

    alternatives = alternatives_collection_type()
    alternatives.put((prefix_type(), expression, table))

    while True:
        try:
            prefix, tail, table = alternatives.pop()
        except alternatives.PopException:
            break
        else:
            alt = AlternativesGenerator(tail, table)
            tail = None
            for head, tail, table in alt:
                prefix_copy = copy(prefix)
                prefix_copy.put(head)
                if tail is EMPTY_STRING:
                    yield prefix_copy, table
                else:
                    alternatives.put((prefix_copy, tail, table))
            if tail is None and not only_complete_words:
                yield prefix, table


def get_language(expression: Expression, table: SymbolsTable | None = None,
                 word_type: type[CollectionWrapper] = WORD_TYPE,
                 alternatives_collection_type: type[CollectionWrapper] = ALTERNATIVES_COLLECTION_TYPE,
                 only_complete_words: bool = ONLY_COMPLETE_WORDS):

    if table is None:
        table = SymbolsTable()

    for prefix, table in _get_alternatives(word_type, expression, table,
                                           alternatives_collection_type,
                                           only_complete_words):
        if not prefix:
            prefix.put(EMPTY_STRING)
            yield prefix
        else:
            for prefix, _ in _get_alternatives(word_type, Concatenation(prefix), table,
                                               alternatives_collection_type,
                                               only_complete_words):
                yield prefix
