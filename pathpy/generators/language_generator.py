from __future__ import annotations
from functools import partial

from pathpy.adts.extensible_iterator import ExtensibleIterator
from pathpy.exceptions import IncompleteMatch, ReificationError
from pathpy.generators.defaults import (ADT_CREATOR, ADT_GET_OP, ADT_PUT_OP,
                                        COMPLETE_WORD,
                                        IGNORE_REIFICATION_ERRORS)

from .alternatives_generator import alts_generator
from .symbols_table import SymbolsTable
from .word_generator import WordGenerator

# TODO: Concurrent-safe version.

__all__ = ['LanguageGenerator']


class LanguageGenerator:
    def __init__(self, expression, symbols_table=None,
                 adt_creator=ADT_CREATOR, adt_get_op=ADT_GET_OP, adt_put_op=ADT_PUT_OP):
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

    def reification(self, word_reifier=WordGenerator.reification, ignore_reification_errors=IGNORE_REIFICATION_ERRORS):
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

    def as_(self, container, word_reifier=partial(WordGenerator.as_, complete_word=COMPLETE_WORD), ignore_reification_errors=IGNORE_REIFICATION_ERRORS):
        return container(self.reification(word_reifier, ignore_reification_errors))

    def as_set_of_tuples(self, complete_words=COMPLETE_WORD, ignore_reification_errors=IGNORE_REIFICATION_ERRORS):
        return set(self.reification(partial(WordGenerator.as_, container=tuple, complete=complete_words), ignore_reification_errors))
