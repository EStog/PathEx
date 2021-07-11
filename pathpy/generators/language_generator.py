from __future__ import annotations

from pathpy.adts.extensible_iterator import ExtensibleIterator
from pathpy.exceptions import IncompleteMatch, ReificationError

from .alternatives_generator import alts_generator
from .symbols_table import SymbolsTable
from .word_generator import WordGenerator

# TODO: Parallel-safe version: put a lock for iter-object exclusivity in `__next__`
# and make set `alternatives` parallel-safe.


def reify_word_as_tuple(x, complete_word):
    return tuple(WordGenerator.reify(x, complete=complete_word))


class LanguageGenerator:
    def __init__(self, expression, symbols_table=None, lock_class=None,
                 adt_creator=list, adt_get_op=list.pop, adt_put_op=list.append):
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

    def reify(self, initial=set(), converter=lambda x: {x},
              add_op=lambda x, y: x | y, word_reifier=reify_word_as_tuple,
              complete_word=True, ignore_reification_errors=False):
        s = initial
        for x in self:
            try:
                x = word_reifier(x, complete=complete_word)
            except IncompleteMatch:
                continue
            except ReificationError:
                if ignore_reification_errors:
                    continue
                else:
                    raise
            s = add_op(s, converter(x))
        return s

    def as_set_of_str(self, complete_word=True, ignore_reification_errors=True):
        return self.reify(word_reifier=WordGenerator.as_str, complete_word=complete_word,
                          ignore_reification_errors=ignore_reification_errors)

    def as_list_of_strs(self, complete_word=True, ignore_reification_errors=True):
        return self.reify(initial=[], converter=lambda x: [x], add_op=lambda x, y: x+y,
                          word_reifier=WordGenerator.as_str, complete_word=complete_word,
                          ignore_reification_errors=ignore_reification_errors)

    def as_list_of_lists(self, complete_word, ignore_reification_errors=True):
        return self.reify(initial=[], converter=lambda x: [x], add_op=lambda x, y: x+y,
                          word_reifier=WordGenerator.reify, complete_word=complete_word,
                          ignore_reification_errors=ignore_reification_errors)


__all__ = ['LanguageGenerator']
