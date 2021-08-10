from __future__ import annotations

from typing import Iterable, Iterator

from pathpy.adts.collection_wrapper import CollectionWrapper
from pathpy.expressions.expression import Expression
from pathpy.generators.alternatives_generator import AlternativesGenerator
from pathpy.generators.defaults import (ALTERNATIVES_COLLECTION_TYPE,
                                        LANGUAGE_TYPE, MAX_LOOKAHEAD, ONLY_COMPLETE_WORDS,
                                        WORD_TYPE, WORDS_COLLECTION_TYPE)
from pathpy.generators.lazy_value import LazyValue

from .letters_generator import LettersGenerator
from .symbols_table import SymbolsTable

# TODO: Concurrent-safe version.

__all__ = ['WordsGenerator']

Alternative = tuple[list[object], AlternativesGenerator]


class WordsGenerator(Iterator[LettersGenerator]):
    def __init__(self, expression: Expression,
                 table: SymbolsTable | None = None,
                 alternatives_collection_type: type[CollectionWrapper] | None = None,
                 delivered_collection_type: type[CollectionWrapper] | None = None,
                 words_collection_type: type[CollectionWrapper] | None = None,
                 max_lookahead: int = MAX_LOOKAHEAD):
        if table is None:
            table = SymbolsTable()
        if alternatives_collection_type is None:
            self._alternatives: CollectionWrapper[Alternative] = \
                ALTERNATIVES_COLLECTION_TYPE()
        else:
            self._alternatives = alternatives_collection_type()
        if delivered_collection_type is None:
            self._delivered: CollectionWrapper[LettersGenerator] = \
                ALTERNATIVES_COLLECTION_TYPE()
        else:
            self._delivered = delivered_collection_type()
        if words_collection_type is None:
            self._words: CollectionWrapper[LettersGenerator] = \
                WORDS_COLLECTION_TYPE()
        else:
            self._words = words_collection_type()
        self._alternatives.put(
            ([], AlternativesGenerator(expression, table)))
        self.max_lookahead = max_lookahead

    def __next__(self) -> LettersGenerator:
        try:
            to_deliver = self._words.pop()
        except self._words.PopException:
            while True:
                try:
                    prefix, alts_gen = self._alternatives.pop()
                except self._alternatives.PopException:
                    if not self._advance_one_delivered():
                        raise StopIteration
                else:
                    to_deliver = LettersGenerator(prefix, alts_gen,
                                                  self, self.max_lookahead)
                    if not to_deliver.exhausted or to_deliver.complete:
                        break
        self._delivered.put(to_deliver)
        return to_deliver

    def _advance_one_delivered(self) -> bool:
        while True:
            try:
                delivered = self._delivered.pop()
            except self._delivered.PopException:
                return False
            else:
                if None not in delivered.advance_once():
                    self._delivered.put(delivered)
                    break
        return True

    def register_alternative(self, prefix, alts_gen):
        self._alternatives.put((prefix, alts_gen))

    def register_words(self, iterable: Iterable):
        self._words.extend(iterable)

    def get_language(self,
                     language_collection_type=LANGUAGE_TYPE,
                     word_collection_type=WORD_TYPE,
                     only_complete_words=ONLY_COMPLETE_WORDS):
        language = language_collection_type()
        for w in self:
            word = word_collection_type()
            for l in w:
                if isinstance(l, LazyValue):
                    l = l.value
                word.put(l)
            if not only_complete_words or w.complete:
                language.put(word)
        return language
