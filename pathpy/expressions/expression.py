from __future__ import annotations

from abc import ABC
from collections import deque
from functools import singledispatchmethod
from math import inf
from typing import cast

from pathpy.adts.cached_generators.cached_generator import CachedGenerator
from pathpy.generators.defaults import (ADT_CREATOR, ADT_GET_OP, ADT_PUT_OP,
                                        COMPLETE_WORD,
                                        IGNORE_REIFICATION_ERRORS)

# from collections.abc import Hashable

# TODO: __str__ y __repr__ de todas las expresiones

# TODO: implementar igualdad estructural en __eq__
# TODO: construir el hash una sola vez en tiempo de construcción de los objetos


class Expression(ABC):  # (Hashable)
    """
    This class represents an abstract Expression. An Expression represents
    a set of tuples of letters, also called strings or words.
    """
    # TODO: Put default arguments as constant.

    def as_set_of_tuples(self, symbols_table=None, adt_creator=ADT_CREATOR,
                         adt_get_op=ADT_GET_OP, adt_put_op=ADT_PUT_OP, cached=False, complete_words=COMPLETE_WORD, ignore_reification_errors=IGNORE_REIFICATION_ERRORS):
        return self.as_language(symbols_table, adt_creator,
                                adt_get_op, adt_put_op, cached).as_set_of_tuples(complete_words, ignore_reification_errors)

    def as_(self, container, word_reifier=None, symbols_table=None, adt_creator=ADT_CREATOR,
            adt_get_op=ADT_GET_OP, adt_put_op=ADT_PUT_OP,
            cached=False, ignore_reification_errors=IGNORE_REIFICATION_ERRORS):
        if word_reifier is None:
            from pathpy.generators.word_generator import WordGenerator
            word_reifier = WordGenerator.as_
        return self.as_language(symbols_table, adt_creator, adt_get_op, adt_put_op,
                                cached).as_(container, word_reifier, ignore_reification_errors)

    def reification(self, symbols_table=None, adt_creator=ADT_CREATOR,
                    adt_get_op=ADT_GET_OP, adt_put_op=ADT_PUT_OP,
                    cached=False, word_reifier=None,
                    ignore_reification_errors=IGNORE_REIFICATION_ERRORS):
        if word_reifier is None:
            from pathpy.generators.word_generator import WordGenerator
            word_reifier = WordGenerator.reification
        return self.as_language(symbols_table, adt_creator, adt_get_op, adt_put_op,
                                cached).reification(word_reifier, ignore_reification_errors)

    def as_language(self, symbols_table=None, adt_creator=deque,
                    adt_get_op=deque.pop, adt_put_op=deque.append, cached=False):
        from pathpy.generators.language_generator import LanguageGenerator
        if cached:
            if not hasattr(self, 'language_generator'):
                self.language_generator = CachedGenerator(LanguageGenerator)(
                    self, symbols_table, adt_creator, adt_get_op, adt_put_op)
            return cast(LanguageGenerator, self.language_generator)
        else:
            return LanguageGenerator(self, symbols_table, adt_creator, adt_get_op, adt_put_op)

    # @staticmethod
    # def flatten(a, b, type_expression):
    #     if isinstance(a, type_expression) and isinstance(b, type_expression):
    #         return type_expression(chain(iter(a), iter(b)))
    #     else:
    #         return type_expression(a, b)

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
