from __future__ import annotations

from functools import partial

from pathpy.adts.extensible_iterator import ExtensibleIterator
from pathpy.exceptions import IncompleteMatch, ReificationError
from pathpy.expressions.terms.empty_string import EMPTY_STRING
from pathpy.expressions.terms.letters_unions.letters_negative_union import \
    LettersNegativeUnion
from pathpy.expressions.terms.letters_unions.letters_possitive_union import \
    LettersPossitiveUnion
from pathpy.expressions.terms.wildcard import Wildcard

from ._expressions._named_wildcard import NamedWildcard
from .alternatives_generator import alts_generator
from .symbols_table import SymbolsTable

# TODO: Parallel-safe version: put a lock for iter-object exclusivity in `__next__`
# and make sets `delivered` and `to_deliver` parallel-safe.


def check_if_reification_possible(x):
    if x is not EMPTY_STRING and isinstance(x, (Wildcard, LettersNegativeUnion)):
        raise ReificationError(f'{x.__class__.__name__} is undeterminable')
    else:
        return x


def to_str_from_iter(iter):
    return ''.join(str(check_if_reification_possible(x)) for x in iter)


INCOMPLETE_MATCH = object()


class WordGenerator:
    """This class is used to generate a string.

    The instances of this class work closely with its parent `LanguageGenerator` instance. The interactions are concurrent-free.
    """

    def __init__(self,
                 prefix: list[object],
                 tail: object, table: SymbolsTable,
                 alternatives, adt_put_op, words: ExtensibleIterator):
        self._prefix = prefix
        self._tail = tail
        self._table = table
        self._alternatives = alternatives
        self._adt_put_op = adt_put_op
        self._words = words
        self._pointer = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._pointer == len(self._prefix):
            self._expand_once()
        x = self._prefix[self._pointer]
        if isinstance(x, NamedWildcard):
            while (y := self._table.get_value(x)) is x:
                try:
                    self._expand_once()
                except StopIteration:
                    break
            if y is not x:
                x = self._decompose_current(y)
        else:
            x = self._decompose_current(x)
        self._pointer += 1
        return x

    def _expand_once(self):
        if self._tail is EMPTY_STRING:
            raise StopIteration
        alts_gen = alts_generator(self._tail, self._table)
        try:
            head, tail, table = next(alts_gen)
        except StopIteration:
            head = INCOMPLETE_MATCH
            self._tail = EMPTY_STRING
            raise IncompleteMatch
        else:
            self._adt_put_op(self._alternatives,
                             (self._prefix.copy(), alts_gen))
            self._tail = tail
            self._table = table
        finally:
            self._prefix.append(head)

    def _decompose_current(self, e):
        if isinstance(e, LettersPossitiveUnion):
            x = next(iter(e.letters))
            prefix = self._prefix[:self._pointer]

            def word_generator_constructor(h, tail, table):
                return WordGenerator(prefix+[h],
                                     tail, table,
                                     self._alternatives,
                                     self._adt_put_op,
                                     self._words)

            if heads := e.letters - {x}:
                self._words.expand(
                    map(partial(word_generator_constructor,
                                tail=self._tail, table=self._table), heads))
            self._prefix[self._pointer] = x
            return x
        else:
            return e

    def reification(self, complete=True):
        try:
            for x in self:
                yield x
        except IncompleteMatch:
            if complete:
                raise

    def as_(self, container=to_str_from_iter, complete=True):
        return container(check_if_reification_possible(x) for x in self.reification(complete=complete))

    __str__ = as_

    def __repr__(self):
        return (f'{self.__class__.__name__}({self._prefix!r}, '
                f'{self._pointer}, {self._tail!r}, {self._table!r}, ...)')
