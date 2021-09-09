from __future__ import annotations

from typing import Generator, TypeVar

from pathex.adts.collection_wrapper import CollectionWrapper
from pathex.expressions.terms.empty_word import EMPTY_WORD
from pathex.machines.decomposers.decomposer import Decomposer

from .defaults import (COLLECTION_TYPE, COMPLETE_WORDS, WORD_MAX_LENGTH,
                       WORD_TYPE)

__all__ = ['words_generator']

#TODO: a more efficient manner of constructing prefixes by using an immutable linked list

def words_generator(expression: object, machine: Decomposer,
                    complete_words: bool = COMPLETE_WORDS,
                    word_max_length: int = WORD_MAX_LENGTH,
                    partial_words_type: type[CollectionWrapper] = COLLECTION_TYPE) -> Generator[tuple, None, None]:

    partial_words = partial_words_type()
    partial_words.put(((), expression))

    while True:
        try:
            prefix, tail = partial_words.pop()
        except partial_words.PopException:
            break
        else:
            alts = machine.transform(tail)
            tail = None
            if word_max_length <= 0 or len(prefix) < word_max_length:
                for head, tail in alts:
                    if head is not EMPTY_WORD:
                        new_prefix = prefix + (head,)
                    else:
                        new_prefix = prefix
                    if tail is EMPTY_WORD:
                        yield new_prefix
                    else:
                        partial_words.put((new_prefix, tail))
            if tail is None and not complete_words:
                yield prefix
