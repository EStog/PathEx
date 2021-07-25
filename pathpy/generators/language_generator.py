from __future__ import annotations

from collections import deque
from functools import partial

from pathpy.adts.extensible_iterator import ExtensibleIterator
from pathpy.exceptions import IncompleteMatch, ReificationError

from .alternatives_generator import alts_generator
from .symbols_table import SymbolsTable
from .word_generator import WordGenerator, check_if_reification_possible

# TODO: Parallel-safe version: put a lock for iter-object exclusivity in `__next__`
# and make set `alternatives` parallel-safe.

__all__ = ['LanguageGenerator']


class LanguageGenerator:
    def __init__(self, expression, symbols_table=None,
                 adt_creator=deque, adt_get_op=deque.pop, adt_put_op=deque.append):
        if symbols_table is None:
            symbols_table = SymbolsTable()
        self._adt_creator = adt_creator
        self._alternatives = adt_creator()
        self._words = ExtensibleIterator()
        self._adt_put_op = adt_put_op
        self._adt_get_op = adt_get_op
        adt_put_op(self._alternatives,
                   ([], alts_generator(expression, symbols_table)))

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self._words)
        except StopIteration:
            while self._alternatives:
                prefix, alt_gen = self._adt_get_op(self._alternatives)
                try:
                    alt_head, tail, table = next(alt_gen)
                except StopIteration:
                    continue
                else:
                    self._adt_put_op(self._alternatives, (prefix, alt_gen))
                    return WordGenerator(prefix+[alt_head], tail, table,
                                         self._alternatives, self._adt_put_op, self._words)
            else:
                raise StopIteration

    def reification(self, word_reifier=WordGenerator.reification, ignore_reification_errors=False):
        for x in self:
            try:
                yield word_reifier(x)
            except IncompleteMatch:
                continue
            except ReificationError:
                if ignore_reification_errors:
                    continue
                else:
                    raise

    def as_(self, container, word_reifier=partial(WordGenerator.as_, complete_word=True), ignore_reification_errors=True):
        return container(self.reification(word_reifier, ignore_reification_errors))
