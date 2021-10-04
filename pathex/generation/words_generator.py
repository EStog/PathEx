from __future__ import annotations

from typing import Iterator

from pathex.adts.collection_wrapper import CollectionWrapper
from pathex.expressions.expression import Expression
from pathex.machines.decomposers.decomposer import Branches, Decomposer

from .defaults import (ALTERNATIVES_TYPE, COLLECTION_TYPE, COMPLETE_WORDS,
                       LANGUAGE_TYPE, WORD_MAX_LENGTH, WORD_TYPE)
from .letters_generator import LettersGenerator

# TODO: Concurrent-safe version.

__all__ = ['WordsGenerator']

Subtree = tuple[list[object], Branches]


class WordsGenerator(Iterator[LettersGenerator]):
    def __init__(self, expression: Expression, decomposer: Decomposer,
                 alternatives_type: type[CollectionWrapper] = ALTERNATIVES_TYPE,
                 delivered_words_type: type[CollectionWrapper] = COLLECTION_TYPE):
        self._decomposer = decomposer
        self._alternatives: CollectionWrapper[tuple[tuple, Branches]] = \
            alternatives_type()
        self._delivered_words: CollectionWrapper[LettersGenerator] = \
            delivered_words_type()
        self._alternatives.put(((), decomposer.transform(expression)))

    def __next__(self) -> LettersGenerator:
        while True:
            try:
                prefix, alternatives = self._alternatives.pop()
            except self._alternatives.PopException:
                if not self._advance_one_delivered():
                    raise StopIteration
            else:
                to_deliver = LettersGenerator(
                    prefix, alternatives, self._decomposer, self)
                if to_deliver not in self._delivered_words and (not to_deliver.exhausted or to_deliver.complete):
                    break
        self._delivered_words.put(to_deliver)
        return to_deliver

    def _advance_one_delivered(self) -> bool:
        while True:
            try:
                delivered = self._delivered_words.pop()
            except self._delivered_words.PopException:
                return False
            else:
                if delivered.advance_once():
                    self._delivered_words.put(delivered)
                    break
        return True

    def register_partial_word(self, prefix, alts_gen):
        self._alternatives.put((prefix, alts_gen))

    def get_language(self,
                     language_collection_type: type[CollectionWrapper] = LANGUAGE_TYPE,
                     word_collection_type: type[CollectionWrapper] = WORD_TYPE,
                     complete_words: bool = COMPLETE_WORDS,
                     word_max_length: int = WORD_MAX_LENGTH):
        language = language_collection_type()
        for w in self:
            word = word_collection_type()
            i = 0
            while word_max_length <= 0 or i < word_max_length:
                try:
                    l = next(w)
                except StopIteration:
                    break
                else:
                    word.put(l)
                    i += 1
            if not complete_words or w.complete:
                language.put(word)
        return language
