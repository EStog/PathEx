from __future__ import annotations

from typing import Iterator

from pathpy.adts.singleton import singleton
from pathpy.expressions.expression import Expression
from pathpy.expressions.terms.empty_string import EMPTY_STRING

from ._expressions._named_wildcard import NamedWildcard
from .alternatives_generator import AlternativesGenerator
from .lazy_value import LazyValue
from .symbols_table import SymbolsTable


@singleton
class IncompleteWord:
    __slots__ = ()


INCOMPLETE_WORD = IncompleteWord()


class LettersGenerator(Iterator[object]):

    def __init__(self, prefix: list[object], alts_gen: AlternativesGenerator,
                 words_generator, max_lookahead: int):
        from .words_generator import WordsGenerator
        self._prefix = prefix
        self._alts_gen = alts_gen
        self._words_generator: WordsGenerator = words_generator
        self.max_lookahead = max_lookahead
        self._pos = 0
        self._complete = False
        self._exhausted = False
        self.advance_once()

    def __next__(self) -> object:
        while self._pos == len(self._prefix):
            if self.advance_once() == (None, None, None):
                raise StopIteration
        ret = self._prefix[self._pos]
        self._pos += 1
        return ret

    def advance_once(self):
        if self._exhausted:
            return None, None, None
        try:
            head, tail, table, extra = next(self._alts_gen)
        except StopIteration:
            self._exhausted = True
            return None, None, None
        else:
            if tail is EMPTY_STRING:
                self._exhausted = True
                self._complete = True
            self._words_generator.register_alternative(self._prefix.copy(),
                                                       self._alts_gen)
            self._alts_gen = AlternativesGenerator(tail, table, extra)
            if isinstance(head, NamedWildcard):
                head = LazyValue(head, tail, table, extra,
                                 len(self._prefix), self,
                                 self.max_lookahead)
            self._prefix.append(head)
            return tail, table, extra

    def update(self, one: object, rest: Iterator[object], pos: int,
               tail: Expression, table: SymbolsTable, extra: object):
        self._prefix[pos] = one
        before = self._prefix[:pos]
        after = self._prefix[pos+1:]
        self._words_generator.register_words(
            LettersGenerator(
                before + [l] + after,
                AlternativesGenerator(tail, table, extra),
                self._words_generator,
                self.max_lookahead) for l in rest)

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
