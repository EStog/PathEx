from __future__ import annotations

from typing import Iterator

from pathex.adts.singleton import singleton
from pathex.expressions.terms.empty_word import EMPTY_WORD

from .machines.machine import Branches, Machine


@singleton
class IncompleteWord:
    __slots__ = ()


INCOMPLETE_WORD = IncompleteWord()


class LettersGenerator(Iterator[object]):

    def __init__(self, prefix: list[object],
                 branches: Branches,
                 machine: Machine, words_generator):
        from .words_generator import WordsGenerator
        self._prefix = prefix
        self._machine = machine
        self._branches = branches
        self._words_generator: WordsGenerator = words_generator
        self._pos = 0
        self._complete = False
        self._exhausted = False
        self.advance_once()

    def __next__(self) -> object:
        if self._pos == len(self._prefix):
            if not self.advance_once():
                raise StopIteration
        ret = self._prefix[self._pos]
        self._pos += 1
        return ret

    def advance_once(self) -> bool:
        if self._exhausted:
            return False
        try:
            head, tail = next(self._branches)
        except StopIteration:
            self._exhausted = True
            return False
        else:
            if tail is EMPTY_WORD:
                self._exhausted = True
                self._complete = True
            self._words_generator.register_partial_word(
                self._prefix.copy(), self._branches)
            self._branches = self._machine.branches(tail)
            self._prefix.append(head)
            return True

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
