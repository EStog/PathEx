from __future__ import annotations

from abc import ABC
from functools import singledispatchmethod
from math import inf

from pathpy.adts.collection_wrapper import (CollectionWrapper,
                                            get_collection_wrapper)
from pathpy.generators.defaults import (LANGUAGE_TYPE,
                                        LANGUAGE_TYPE, ONLY_COMPLETE_WORDS,
                                        WORD_TYPE)
from pathpy.generators.misc import MAX_LOOKAHEAD

# from collections.abc import Hashable

# TODO: __str__ y __repr__ de todas las expresiones

# TODO: implementar igualdad estructural en __eq__
# TODO: construir el hash una sola vez en tiempo de construcción de los objetos


class Expression(ABC):  # (Hashable)
    """
    This class represents an abstract Expression. An Expression represents
    a set of tuples of letters, also called strings or words.
    """

    def get_generator(self, max_lookahead: int = MAX_LOOKAHEAD):
        from pathpy.generators.words_generator import WordsGenerator
        return WordsGenerator(self, max_lookahead=max_lookahead)

    def get_language(self,
                     language_type=LANGUAGE_TYPE,
                     word_type=WORD_TYPE,
                     only_complete_words=ONLY_COMPLETE_WORDS):
        from pathpy.generators.eager import get_language
        language = language_type()
        for w in get_language(self, word_type=word_type, only_complete_words=only_complete_words):
            language.put(w)
        return language

    # self | other
    @singledispatchmethod
    def __or__(self, other: object) -> Expression:
        from pathpy import Union
        return Union(self, other)

    # self|interable
    @__or__.register(list)
    def __(self, iterable):
        from pathpy import Union, multiplication
        return multiplication(self, Union, iterable)

    # other | self
    # iterable|self
    __ror__ = __or__

    # self & other
    @singledispatchmethod
    def __and__(self, other: object) -> Expression:
        from pathpy import Intersection
        return Intersection(self, other)

    # self&iterable
    @__and__.register(list)
    def __(self, iterable):
        from pathpy import Intersection, multiplication
        return multiplication(self, Intersection, iterable)

    # other & self
    # iterable&self
    __rand__ = __and__

    # self @ other
    @singledispatchmethod
    def __matmul__(self, other: object) -> Expression:
        from pathpy import Synchronization
        return Synchronization(self, other)

    # self@iterable
    @__matmul__.register(list)
    def __(self, iterable):
        from pathpy import Synchronization, multiplication
        return multiplication(self, Synchronization, iterable)

    # other @ self
    # iterable@self
    __rmatmul__ = __matmul__

    # self ^ other
    @singledispatchmethod
    def __xor__(self, other: object) -> Expression:
        from pathpy import symmetric_difference
        return symmetric_difference(self, other)

    # self^iterable
    @__xor__.register(list)
    def __(self, iterable):
        from pathpy import multiplication, symmetric_difference
        return multiplication(self, symmetric_difference, iterable)

    # other ^ self
    # iterable^self
    __rxor__ = __xor__

    # self - other
    @singledispatchmethod
    def __sub__(self, other: object) -> Expression:
        from pathpy import difference
        return difference(self, other)

    # self-iterable
    @__sub__.register(list)
    def __(self, iterable):
        from pathpy import difference, multiplication
        return multiplication(self, difference, iterable)

    # other - self
    @singledispatchmethod
    def __rsub__(self, other: object) -> Expression:
        from pathpy import difference
        return difference(other, self)

    # iterable-self
    @__rsub__.register(list)
    def __rsub__(self, iterable):
        from pathpy import difference, multiplication

        # TODO: replace by left multiplication
        return multiplication(self, difference, iterable)

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
    def __add__(self, other: object) -> Expression:
        from pathpy import Concatenation
        return Concatenation(self, other)

    # self+number
    @__add__.register(int)
    @__add__.register(float)
    @__add__.register(type(...))
    def __(self, number):
        from pathpy import ConcatenationRepetition
        if number is ...:
            number = inf
        return ConcatenationRepetition(self, number, number)

    # self+iterable
    @__add__.register(list)
    def __(self, iterable):
        from pathpy import Concatenation, multiplication
        return multiplication(self, Concatenation, iterable)

    # other + self
    @singledispatchmethod
    def __radd__(self, other: object) -> Expression:
        from pathpy import Concatenation
        return Concatenation(other, self)

    # number+self
    __radd__.register(int, __add__.dispatcher.dispatch(int))
    __radd__.register(float, __add__.dispatcher.dispatch(float))
    __radd__.register(type(...), __add__.dispatcher.dispatch(type(...)))

    # iterable+self
    __radd__.register(list, __add__.dispatcher.dispatch(list))

    # +self
    def __pos__(self):
        from pathpy import ConcatenationRepetition
        return ConcatenationRepetition(self, 1, inf)

    # self * other
    @singledispatchmethod
    def __mul__(self, other: object) -> Expression:
        from pathpy import Concatenation, ConcatenationRepetition
        return Concatenation(ConcatenationRepetition(self, 0, 1), other)

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
        return Concatenation(ConcatenationRepetition(other, 0, 1), self)

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
        return Shuffle(self, other)

    # self//number
    @__floordiv__.register(int)
    @__floordiv__.register(float)
    @__floordiv__.register(type(...))
    def __(self, number):
        from pathpy import ShuffleRepetition
        if number is ...:
            number = inf
        return ShuffleRepetition(self, number, number)

    # self//iterable
    @__floordiv__.register(list)
    def __(self, iterable):
        from pathpy import Shuffle, multiplication
        return multiplication(self, Shuffle, iterable)

    # other // self
    # number//self
    # iterable//other
    __rfloordiv__ = __floordiv__

    # self % other
    @singledispatchmethod
    def __mod__(self, other: object) -> Expression:
        from pathpy import ConcatenationRepetition, Shuffle
        return Shuffle(ConcatenationRepetition(self, 0, 1), other)

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
        return Shuffle(ConcatenationRepetition(other, 0, 1), self)

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

    # self[dictionary]
    @__getitem__.register
    def __(self, dictionary: dict):
        from pathpy import Substitution
        return Substitution(self, dictionary)

    # self[slices]
    @__getitem__.register(tuple)
    def __(self, slices: tuple[slice, ...]):
        from pathpy import Substitution
        d = {}
        for s in slices:
            d[s.start] = s.stop
        return Substitution(self, d)


__all__ = ['Expression']
