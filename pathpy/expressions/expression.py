"""
.. sectionauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>
.. codeauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>
"""

from __future__ import annotations

from abc import ABC
from functools import singledispatchmethod
from math import inf

from pathpy.generators.defaults import (LANGUAGE_TYPE, MAX_LOOKAHEAD,
                                        ONLY_COMPLETE_WORDS, WORD_TYPE)

# TODO: __str__ y __repr__ de todas las expresiones

# TODO: implementar igualdad estructural en __eq__
# TODO: construir el hash una sola vez en tiempo de construcción de los objetos

__all__ = ['Expression']


class Expression(ABC):
    """Abstract base class of expressions."""

    def get_generator(self, extra: object = None, max_lookahead: int = MAX_LOOKAHEAD):
        from pathpy.generators.symbols_table import SymbolsTable
        from pathpy.generators.words_generator import WordsGenerator
        return WordsGenerator(self, SymbolsTable(), extra, max_lookahead=max_lookahead)

    def get_language(self,
                     language_type=LANGUAGE_TYPE,
                     word_type=WORD_TYPE,
                     only_complete_words=ONLY_COMPLETE_WORDS,
                     extra: object = None):
        from pathpy.generators.eager import get_language
        from pathpy.generators.symbols_table import SymbolsTable
        language = language_type()
        for w in get_language(self, SymbolsTable(), extra, word_type=word_type,
                              only_complete_words=only_complete_words):
            language.put(w)
        return language

    # self | other
    @singledispatchmethod
    def __or__(self, other: object) -> Expression:
        from pathpy import Union
        return Union.new(self, other)

    # other | self
    __ror__ = __or__

    # self & other
    @singledispatchmethod
    def __and__(self, other: object) -> Expression:
        from pathpy import Intersection
        return Intersection.new(self, other)

    # other & self
    __rand__ = __and__

    # self @ other
    @singledispatchmethod
    def __matmul__(self, other: object) -> Expression:
        from pathpy import Synchronization
        return Synchronization.new(self, other)

    # other @ self
    __rmatmul__ = __matmul__

    # self ^ other
    @singledispatchmethod
    def __xor__(self, other: object) -> Expression:
        from pathpy import symmetric_difference
        return symmetric_difference(self, other)

    # other ^ self
    __rxor__ = __xor__

    # self - other
    @singledispatchmethod
    def __sub__(self, other: object) -> Expression:
        from pathpy import difference
        return difference(self, other)

    # other - self
    @singledispatchmethod
    def __rsub__(self, other: object) -> Expression:
        from pathpy import difference
        return difference(other, self)

    # -self
    def __neg__(self):
        from pathpy import (LettersNegativeUnion, LettersPossitiveUnion,
                            Negation)
        if isinstance(self, LettersPossitiveUnion):
            return LettersNegativeUnion(self.letters)
        elif isinstance(self, LettersNegativeUnion):
            return LettersPossitiveUnion(self.letters)
        else:
            return Negation(self)

    # self + other
    @singledispatchmethod
    def __add__(self, other: object) -> Concatenation:
        """Sum operation (``+``) is used to specify :class:`~.Concatenation` and :class:`~.ConcatenationRepetition` expression types.

        .. testsetup:: *

            >>> from pathpy.expressions.aliases import *
            >>> from pathpy import Concatenation, ConcatenationRepetition
            >>> from math import inf

        With an :class:`int` it translate to :class:`~.ConcatenationRepetition`:

        >>> assert L('a') + 4 == ConcatenationRepetition(L('a'), 4, 4)

        With any other object it translate to :class:`~.Concatenation`:

        >>> assert L('a') + 'e' == Concatenation(L('a'), 'e')
        """
        from pathpy import Concatenation
        return Concatenation.new(self, other)

    # self+number
    @__add__.register(int)
    def __(self, number) -> ConcatenationRepetition:
        from pathpy import ConcatenationRepetition
        if number is ...:
            number = inf
        return ConcatenationRepetition(self, number, number)

    # other + self
    @singledispatchmethod
    def __radd__(self, other: object) -> Expression:
        from pathpy import Concatenation
        return Concatenation.new(other, self)

    # number+self
    __radd__.register(int, __add__.dispatcher.dispatch(int))
    __radd__.register(float, __add__.dispatcher.dispatch(float))
    __radd__.register(type(...), __add__.dispatcher.dispatch(type(...)))

    # +self
    def __pos__(self):
        from pathpy import ConcatenationRepetition
        return ConcatenationRepetition(self, 1, inf)

    # self * other
    @singledispatchmethod
    def __mul__(self, other: object) -> Expression:
        from pathpy import Concatenation, ConcatenationRepetition
        return Concatenation.new(ConcatenationRepetition(self, 0, 1), other)

    # self*number
    @__mul__.register(int)
    @__mul__.register(float)
    @__mul__.register(type(...))
    def __(self, number):
        from pathpy import ConcatenationRepetition
        if number is ...:
            number = inf
        return ConcatenationRepetition(self, 0, number)

    # self*[lb,ub]
    @__mul__.register
    def __(self, bounds: list):
        from pathpy import ConcatenationRepetition
        return ConcatenationRepetition(self, *bounds)

    # other * self
    @singledispatchmethod
    def __rmul__(self, other: object) -> Expression:
        from pathpy import Concatenation, ConcatenationRepetition
        return Concatenation.new(ConcatenationRepetition(other, 0, 1), self)

    # number*self
    __rmul__.register(int, __mul__.dispatcher.dispatch(int))
    __rmul__.register(float, __mul__.dispatcher.dispatch(float))
    __rmul__.register(type(...), __mul__.dispatcher.dispatch(type(...)))

    # [lb,ub]*self
    __rmul__.register(list, __mul__.dispatcher.dispatch(list))

    # self // other
    @singledispatchmethod
    def __floordiv__(self, other: object) -> Expression:
        from pathpy import Shuffle
        return Shuffle.new(self, other)

    # self//number
    @__floordiv__.register(int)
    @__floordiv__.register(float)
    @__floordiv__.register(type(...))
    def __(self, number):
        from pathpy import ShuffleRepetition
        if number is ...:
            number = inf
        return ShuffleRepetition(self, number, number)

    # other // self
    # number//self
    __rfloordiv__ = __floordiv__

    # self % other
    @singledispatchmethod
    def __mod__(self, other: object) -> Expression:
        from pathpy import ConcatenationRepetition, Shuffle
        return Shuffle.new(ConcatenationRepetition(self, 0, 1), other)

    # self%number
    @__mod__.register(int)
    @__mod__.register(float)
    @__mod__.register(type(...))
    def __(self, number):
        from pathpy import ShuffleRepetition
        if number is ...:
            number = inf
        return ShuffleRepetition(self, 0, number)

    # self%[lb, ub]
    @__mod__.register
    def __(self, bounds: list):
        from pathpy import ShuffleRepetition
        return ShuffleRepetition(self, *bounds)

    # other % self
    @singledispatchmethod
    def __rmod__(self, other: object) -> Expression:
        from pathpy import ConcatenationRepetition, Shuffle
        return Shuffle.new(ConcatenationRepetition(other, 0, 1), self)

    __rmod__.register(int, __mod__.dispatcher.dispatch(int))
    __rmod__.register(float, __mod__.dispatcher.dispatch(float))
    __rmod__.register(type(...), __mod__.dispatcher.dispatch(type(...)))

    # [lb,ub]%self
    __rmod__.register(list, __mod__.dispatcher.dispatch(list))

    @singledispatchmethod
    def __getitem__(self, key: object) -> Expression:
        raise TypeError('Key schema not supported')

    # self[slice]
    @__getitem__.register
    def __(self, slice: slice):
        assert slice.step == None, 'Step must be None'
        from pathpy import Substitution
        return Substitution(self, {slice.start: slice.stop})

    # self[slices]
    @__getitem__.register(tuple)
    def __(self, slices: tuple[slice, ...]):
        from pathpy import Substitution
        d = {}
        for s in slices:
            d[s.start] = s.stop
        return Substitution(self, d)
