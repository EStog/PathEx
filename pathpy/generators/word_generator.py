from __future__ import annotations

from functools import partial, singledispatchmethod

from pathpy.adts.extensible_iterator import ExtensibleIterator
from pathpy.adts.singleton import singleton
from pathpy.exceptions import ReificationError
from pathpy.expressions.expression import Expression
from pathpy.expressions.terms.empty_string import EMPTY_STRING
from pathpy.expressions.terms.letters_unions.letters_possitive_union import \
    LettersPossitiveUnion

from ._expressions._named_wildcard import NamedWildcard
from .alternatives_generator import alts_generator
from .symbols_table import SymbolsTable

# TODO: Parallel-safe version: put a lock for iter-object exclusivity in `__next__`
# and make sets `delivered` and `to_deliver` parallel-safe.


@singleton
class NoCompleteMatch:
    @singledispatchmethod
    def __add__(self, other: str):
        return ''

    @__add__.register
    def __(self, other: tuple):
        return ()


NO_COMPLETE_MATCH = NoCompleteMatch()


def _converter(x):
    if x is not EMPTY_STRING and isinstance(x, Expression):
        raise ReificationError(f'{x.__class__.__name__} is undeterminable')
    else:
        return str(x)


class WordGenerator:
    """This class is used to generate a string.

    The instances of this class work closely with its parent `LanguageGenerator` instance. The interactions are concurrent-free.
    """

    def __init__(self,
                 prefix: tuple[object, ...],
                 h: object, suffix: tuple[object, ...],
                 tail: object, table: SymbolsTable,
                 alternatives, adt_put_op,  words: ExtensibleIterator, ):
        self._tail = tail
        self._table = table
        self._alternatives = alternatives
        self._adt_put_op = adt_put_op
        self._words = words
        self._pointer = 0
        self._update_prefix(prefix, h, suffix)

    def __iter__(self):
        return self

    def __next__(self):
        if self._pointer == len(self._prefix):
            self.expand_head()

        if (isinstance(x := self._prefix[self._pointer], NamedWildcard) and
                self._table.get_value(x) is x):
            try:
                self.expand_head()
            except StopIteration:
                pass

        x = self._prefix[self._pointer]
        if isinstance(x, NamedWildcard):
            x = self._table.get_value(x)
        self._pointer += 1
        return x

    def expand_head(self):
        self._expand_once()
        x = self._prefix[self._pointer]
        y = None
        if isinstance(x, NamedWildcard):
            while (y := self._table.get_value(x)) is x:
                try:
                    self._expand_once()
                except StopIteration:
                    break
        if y:
            prefix = self._prefix[:self._pointer]
            suffix = self._prefix[self._pointer+1:]
            self._update_prefix(prefix, y, suffix)

    def _expand_once(self):
        if self._tail is EMPTY_STRING:
            raise StopIteration
        alts_gen = alts_generator(self._tail, self._table)
        try:
            head, tail, table = next(alts_gen)
        except StopIteration:
            x = NO_COMPLETE_MATCH
            self._prefix += (x,)
            self._tail = EMPTY_STRING
        else:
            self._adt_put_op(self._alternatives, (self._prefix, alts_gen))
            self._tail = tail
            self._table = table
            self._update_prefix(self._prefix, head, ())

    def _update_prefix(self, prefix, head, suffix):
        if isinstance(head, LettersPossitiveUnion):
            x = next(iter(head.letters))

            def word_generator_constructor(h, tail, table):
                return WordGenerator(prefix, h, suffix,
                                     tail, table,
                                     self._alternatives,
                                     self._adt_put_op,
                                     self._words)

            if heads := head.letters - {x}:
                self._words.expand(map(
                    partial(word_generator_constructor, tail=self._tail, table=self._table), heads))
        else:
            x = head
        self._prefix = prefix + (x,) + suffix

    def reify(self, initial='', converter=_converter,
              add_op=lambda x, y: x + y, complete=True):
        s = initial
        for x in self:
            if x is NO_COMPLETE_MATCH:
                return NO_COMPLETE_MATCH if complete else s
            else:
                s = add_op(s, converter(x))
        return s

    def as_tuple(self, complete=True):
        return self.reify((), lambda x: (x,), complete=complete)

    def __repr__(self):
        return (f'{self.__class__.__name__}({self._prefix!r}, '
                f'{self._pointer}, {self._tail!r}, {self._table!r}, ...)')
