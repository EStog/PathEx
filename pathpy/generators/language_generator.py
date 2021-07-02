from __future__ import annotations

from pathpy.adts.extensible_iterator import ExtensibleIterator

from .alternatives_generator import alts_generator
from .symbols_table import SymbolsTable
from .word_generator import NO_COMPLETE_MATCH, WordGenerator

# TODO: Parallel-safe version: put a lock for iter-object exclusivity in `__next__`
# and make set `alternatives` parallel-safe.


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
                   ((), alts_generator(expression, symbols_table)))

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
                    return WordGenerator(prefix, alt_head, (), tail, table,
                                         self._alternatives, self._adt_put_op, self._words)
            else:
                raise StopIteration

    def reify(self, initial=frozenset(), converter=lambda x: {x},
              add_op=lambda x, y: x | y, word_reifier=WordGenerator.reify,
              complete=True):
        s = initial
        for x in self:
            x = word_reifier(x, complete=complete)
            if x is not NO_COMPLETE_MATCH:
                s = add_op(s, converter(x))
        return s

    def as_set_of_tuples(self, complete=True):
        return self.reify(word_reifier=WordGenerator.as_tuple, complete=complete)

    def as_tuple_of_strs(self, complete=True):
        return self.reify((), lambda x: (x, ), lambda x, y: x+y, complete=complete)

    def as_tuple_of_tuples(self, complete):
        return self.reify((), lambda x: (x, ), lambda x, y: x+y, WordGenerator.as_tuple, complete=complete)


__all__ = ['LanguageGenerator']
