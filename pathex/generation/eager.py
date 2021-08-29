from __future__ import annotations

from copy import copy

from pathex.adts.collection_wrapper import CollectionWrapper
from pathex.expressions.expression import Expression
from pathex.expressions.terms.empty_word import EMPTY_WORD
from pathex.generation.machines.machine import Machine

from .defaults import (COLLECTION_TYPE, ONLY_COMPLETE_WORDS, WORD_MAX_LENGTH,
                       WORD_TYPE)

__all__ = ['words_generator']


def words_generator(
        expression: Expression, machine: Machine,
        word_type: type[CollectionWrapper] = WORD_TYPE,
        only_complete_words: bool = ONLY_COMPLETE_WORDS,
        word_max_length: int = WORD_MAX_LENGTH,
        partial_words_type: type[CollectionWrapper] = COLLECTION_TYPE):

    partial_words = partial_words_type()
    partial_words.put((word_type(), expression))

    while True:
        try:
            prefix, tail = partial_words.pop()
        except partial_words.PopException:
            break
        else:
            alt = machine.branches(tail)
            tail = None
            for head, tail in alt:
                prefix_copy = copy(prefix)
                prefix_copy.put(head)
                if tail is EMPTY_WORD:
                    yield prefix_copy
                else:
                    partial_words.put((prefix_copy, tail))
            if tail is None and not only_complete_words:
                if not prefix:
                    yield EMPTY_WORD
                else:
                    yield prefix
