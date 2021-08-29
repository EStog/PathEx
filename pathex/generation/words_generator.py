from __future__ import annotations

from typing import Iterator

from pathex.adts.collection_wrapper import CollectionWrapper
from pathex.expressions.expression import Expression
from pathex.generation.machines.machine import Branches, Machine

from .defaults import (COLLECTION_TYPE, LANGUAGE_TYPE, ONLY_COMPLETE_WORDS,
                       WORD_MAX_LENGTH, WORD_TYPE)
from .letters_generator import LettersGenerator

# TODO: Concurrent-safe version.

__all__ = ['WordsGenerator']

Subtree = tuple[list[object], Branches]


class WordsGenerator(Iterator[LettersGenerator]):
    def __init__(self, expression: Expression, machine: Machine,
                 partial_words_type: type[CollectionWrapper] | None = None,
                 delivered_words_type: type[CollectionWrapper] | None = None):
        self._machine = machine
        if partial_words_type is None:
            self._partial_words: CollectionWrapper[Subtree] = \
                COLLECTION_TYPE()
        else:
            self._partial_words = partial_words_type()
        if delivered_words_type is None:
            self._delivered_words: CollectionWrapper[LettersGenerator] = \
                COLLECTION_TYPE()
        else:
            self._delivered_words = delivered_words_type()
        self._partial_words.put(
            ([], machine.branches(expression)))

    def __next__(self) -> LettersGenerator:
        while True:
            try:
                prefix, alternatives = self._partial_words.pop()
            except self._partial_words.PopException:
                if not self._advance_one_delivered():
                    raise StopIteration
            else:
                to_deliver = LettersGenerator(
                    prefix, alternatives, self._machine, self)
                if not to_deliver.exhausted or to_deliver.complete:
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
        self._partial_words.put((prefix, alts_gen))

    def get_language(self,
                     language_collection_type=LANGUAGE_TYPE,
                     word_collection_type=WORD_TYPE,
                     only_complete_words: bool = ONLY_COMPLETE_WORDS,
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
            if not only_complete_words or w.complete:
                language.put(word)
        return language
