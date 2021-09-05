from __future__ import annotations

from copy import copy
from typing import Generator, Iterator, TypeVar

from pathex.adts.collection_wrapper import CollectionWrapper
from pathex.expressions.expression import Expression
from pathex.expressions.terms.empty_word import EMPTY_WORD
from pathex.generation.machines.machine import Machine

from .defaults import (COLLECTION_TYPE, COMPLETE_WORDS, WORD_MAX_LENGTH,
                       WORD_TYPE)

__all__ = ['words_generator']

T = TypeVar('T', bound=CollectionWrapper)


def words_generator(expression: Expression, machine: Machine,
                    word_type: type[T] = WORD_TYPE,
                    complete_words: bool = COMPLETE_WORDS,
                    word_max_length: int = WORD_MAX_LENGTH,
                    partial_words_type: type[CollectionWrapper] = COLLECTION_TYPE) -> Generator[T, None, None]:

    partial_words = partial_words_type()
    partial_words.put((word_type(), expression))

    while True:
        try:
            prefix, tail = partial_words.pop()
        except partial_words.PopException:
            break
        else:
            alts = machine.branches(tail)
            tail = None
            if word_max_length <= 0 or len(prefix) < word_max_length:
                for head, tail in alts:
                    prefix_copy = copy(prefix)
                    if head is not EMPTY_WORD:
                        prefix_copy.put(head)
                    if tail is EMPTY_WORD:
                        yield prefix_copy
                    else:
                        partial_words.put((prefix_copy, tail))
            if tail is None and not complete_words:
                yield prefix
