from __future__ import annotations

from typing import Iterator

from pathex.adts.singleton import singleton
from pathex.expressions.terms.empty_word import EMPTY_WORD
from pathex.machines.decomposers.decomposer import Branches, Decomposer


@singleton
class IncompleteWord:
    __slots__ = ()


INCOMPLETE_WORD = IncompleteWord()


class LettersGenerator(Iterator[object]):

    def __init__(self, prefix: tuple,
                 branches: Branches,
                 decomposer: Decomposer, words_generator):
        from .words_generator import WordsGenerator
        self._prefix = prefix
        self._decomposed = decomposer
        self._branches = branches
        self._words_generator: WordsGenerator = words_generator
        self._pos = 0
        self._complete = False
        self._exhausted = False
        self._initial_tail = self.advance_once()
        self._initial_prefix = self._prefix

    def __next__(self) -> object:
        while self._pos == len(self._prefix):
            if not self.advance_once():
                raise StopIteration
        ret = self._prefix[self._pos]
        self._pos += 1
        return ret

    def advance_once(self) -> object:
        if self._exhausted:
            return False
        try:
            head, tail = next(self._branches)
        except StopIteration:
            self._exhausted = True
            return False
        else:
            self._words_generator.register_partial_word(
                self._prefix, self._branches)
            if tail is EMPTY_WORD:
                self._exhausted = True
                self._complete = True
            else:
                self._branches = self._decomposed.transform(tail)
            if head is not EMPTY_WORD:
                self._prefix += (head,)
            return tail

    @property
    def exhausted(self):
        return self._exhausted

    @property
    def complete(self):
        return self._complete

    def _set_complete(self):
        self._complete = True

    def restart(self):
        self._pos = 0

    def __str__(self) -> str:
        return ''.join(str(l) for l in self)

    def __eq__(self, other):
        if isinstance(other, LettersGenerator):
            return (self._initial_prefix, self._initial_tail) == (other._initial_prefix, other._initial_tail)
        else:
            return False

    def __hash__(self):
        return hash((self._initial_prefix, self._initial_tail))
