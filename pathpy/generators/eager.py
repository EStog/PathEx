from __future__ import annotations

from collections import deque
from typing import Callable, Iterable

from pathpy.adts.collection_wrapper import (CollectionWrapper,
                                            get_collection_wrapper)
from pathpy.expressions.expression import Expression
from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.terms.empty_string import EMPTY_STRING

from .alternatives_generator import AlternativesGenerator
from .symbols_table import SymbolsTable


def _get_clean_alternatives(
        expression: Expression, table: SymbolsTable,
        alternatives_collection_type: type[CollectionWrapper],
        only_complete_words: bool):

    alternatives = alternatives_collection_type()
    alternatives.put(([], expression, table))

    while True:
        try:
            prefix, tail, table = alternatives.pop()
        except alternatives.PopException:
            break
        else:
            alt = AlternativesGenerator(tail, table)
            tail = None
            for head, tail, table in alt:
                if tail is EMPTY_STRING:
                    yield prefix + [head], table
                else:
                    alternatives.put((prefix+[head], tail, table))
            if tail is None and not only_complete_words:
                yield prefix, table


def _init(table: SymbolsTable | None = None,
          word_type: Callable[[Iterable[object]], object] | None = None,
          alternatives_collection_type: type[CollectionWrapper] | None = None):
    if table is None:
        table = SymbolsTable()
    if word_type is None:
        def word_type(coll): return ''.join(str(x) for x in coll)
    if alternatives_collection_type is None:
        alternatives_collection_type = get_collection_wrapper(
            deque, deque.appendleft, deque.extendleft, deque.popleft, IndexError)
    return table, word_type, alternatives_collection_type


def get_language(expression: Expression, table: SymbolsTable | None = None,
                 word_type: Callable[[Iterable[object]], object] | None = None,
                 alternatives_collection_type: type[CollectionWrapper] | None = None,
                 only_complete_words: bool = True):

    table, word_type, alternatives_collection_type = _init(
        table, word_type, alternatives_collection_type)

    for prefix, table in _get_clean_alternatives(expression, table,
                                                 alternatives_collection_type,
                                                 only_complete_words):
        for prefix, _ in _get_clean_alternatives(Concatenation(prefix), table,
                                                 alternatives_collection_type,
                                                 only_complete_words):
            yield word_type(prefix)
