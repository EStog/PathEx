"""
.. sectionauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>
.. codeauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>
"""

from __future__ import annotations

from abc import ABC
from functools import singledispatchmethod
from math import inf

from pathex.generation.defaults import (LANGUAGE_TYPE, ONLY_COMPLETE_WORDS,
                                        WORD_TYPE)
from pathex.generation.machines.machine import Machine

# TODO: __str__ y __repr__ de todas las expresiones

__all__ = ['Expression']

ellipsis = type(...)


class Expression(ABC):
    """Abstract base class of expressions."""

    def get_generator(self, machine: Machine | None = None):
        if machine is None:
            from pathex.generation.machines.extended_machine_with_complemented_singwords import \
                ExtendedMachineWithComplementedSingWords
            machine = ExtendedMachineWithComplementedSingWords()
        from pathex.generation.words_generator import WordsGenerator
        return WordsGenerator(self, machine)

    def get_eager_generator(self, machine: Machine | None = None,
                            word_type=WORD_TYPE,
                            only_complete_words=ONLY_COMPLETE_WORDS):
        if machine is None:
            from pathex.generation.machines.extended_machine_with_complemented_singwords import \
                ExtendedMachineWithComplementedSingWords
            machine = ExtendedMachineWithComplementedSingWords()
        from pathex.generation.eager import words_generator
        return words_generator(self, machine, word_type, only_complete_words)

    def get_language(self,
                     language_type=LANGUAGE_TYPE,
                     word_type=WORD_TYPE,
                     only_complete_words=ONLY_COMPLETE_WORDS,
                     machine: Machine | None = None,):
        if machine is None:
            from pathex.generation.machines.extended_machine_with_complemented_singwords import \
                ExtendedMachineWithComplementedSingWords
            machine = ExtendedMachineWithComplementedSingWords()
        from pathex.generation.eager import words_generator
        language = language_type()
        for w in words_generator(self, machine, word_type, only_complete_words=only_complete_words):
            language.put(w)
        return language

    # self | other
    @singledispatchmethod
    def __or__(self, other: object) -> Expression:
        from pathex import Union
        return Union.new(self, other)

    # other | self
    __ror__ = __or__

    # self & other
    @singledispatchmethod
    def __and__(self, other: object) -> Expression:
        from pathex import Intersection
        return Intersection.new(self, other)

    # other & self
    __rand__ = __and__

    # self @ other
    @singledispatchmethod
    def __matmul__(self, other: object) -> Expression:
        from pathex import Synchronization
        return Synchronization.new(self, other)

    # other @ self
    __rmatmul__ = __matmul__

    # self ^ other
    # @singledispatchmethod
    # def __xor__(self, other: object) -> Expression:
    #     from pathex import symmetric_difference
    #     return symmetric_difference(self, other)

    # other ^ self
    # __rxor__ = __xor__

    # self - other
    @singledispatchmethod
    def __sub__(self, other: object) -> Expression:
        from pathex import Difference
        return Difference.new(self, other)

    # other - self
    @singledispatchmethod
    def __rsub__(self, other: object) -> Expression:
        from pathex import Difference
        return Difference.new(other, self)

    # self + other
    @singledispatchmethod
    def __add__(self, other: object) -> 'Concatenation':
        """Plus symbol (``+``) is used to construct :class:`~.Concatenation` and :class:`~.ConcatenationRepetition` expressions instances.

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Concatenation, ConcatenationRepetition

        With an :class:`int` as operand it construct a :class:`~.ConcatenationRepetition`:

        >>> assert L('a')+4 == ConcatenationRepetition(L('a'), 4, 4)

        With any other object as operand it constructs a :class:`~.Concatenation`:

        >>> assert L('a') + 'e' == Concatenation(L('a'), 'e')
        """
        from pathex import Concatenation
        return Concatenation.new(self, other)

    # self+number
    @__add__.register(int)
    def __(self, number) -> 'ConcatenationRepetition':
        from pathex import ConcatenationRepetition
        return ConcatenationRepetition(self, number, number)

    # other + self
    @singledispatchmethod
    def __radd__(self, other: object) -> 'Concatenation':
        """This is the same as :meth:`__add__`, except when it is used to construct :class:`~.Concatenation` because the former is not commutative.

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Concatenation

        For example:

        >>> exp1 = L('a') + 's'
        >>> exp2 = 's' + L('a')
        >>> assert exp1 != exp2
        >>> assert exp1 == Concatenation(L('a'), 's')
        >>> assert exp2 == Concatenation('s', L('a'))
        """
        from pathex import Concatenation
        return Concatenation.new(other, self)

    # number+self
    __radd__.register(int, __add__.dispatcher.dispatch(int))

    # +self
    def __pos__(self):
        from pathex import ConcatenationRepetition
        return ConcatenationRepetition(self, 1, inf)

    # self * other
    @singledispatchmethod
    def __mul__(self, other: object) -> 'Concatenation':
        """Asterisk symbol (``*``) is used to construct an optional :class:`~.Concatenation` and :class:`~.ConcatenationRepetition` expressions instances.

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Concatenation, ConcatenationRepetition
            >>> from math import inf

        With any of :class:`list` of two boundaries, an :class:`int`, :obj:`math.inf` or :data:`Ellipsis` as operand it constructs a :class:`~.ConcatenationRepetition`:

        >>> assert L('a')*[2,5] == ConcatenationRepetition(L('a'), 2, 5)
        >>> assert L('a')*4 == L('a')*[0,4] == ConcatenationRepetition(L('a'), 0, 4)
        >>> assert L('a')*inf == L('a')*... == ConcatenationRepetition(L('a'), 0, inf)

        With any other object as operand it constructs an optional :class:`~.Concatenation`:

        >>> assert L('a') * 'e' == Concatenation(ConcatenationRepetition(L('a'), 0, 1), 'e')
        """
        from pathex import Concatenation, ConcatenationRepetition
        return Concatenation.new(ConcatenationRepetition(self, 0, 1), other)

    # self*[lb,ub]
    @__mul__.register(list)
    def __(self, bounds) -> 'ConcatenationRepetition':
        from pathex import ConcatenationRepetition
        return ConcatenationRepetition(self, *bounds)

    # self*number
    @__mul__.register(int)
    @__mul__.register(float)
    @__mul__.register(ellipsis)
    def __(self, number) -> 'ConcatenationRepetition':
        from pathex import ConcatenationRepetition
        return ConcatenationRepetition(self, 0, number)

    # other * self
    @singledispatchmethod
    def __rmul__(self, other: object) -> 'Concatenation':
        """This is the same as :meth:`__mul__`, except when it is used to construct :class:`~.Concatenation` because the former is not commutative.

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Concatenation, ConcatenationRepetition

        For example:

        >>> exp1 = L('a') * 's'
        >>> exp2 = 's' * L('a')
        >>> assert exp1 != exp2
        >>> assert exp1 == Concatenation(ConcatenationRepetition(L('a'), 0, 1), 's')
        >>> assert exp2 == Concatenation(ConcatenationRepetition('s', 0, 1), L('a'))
        """
        from pathex import Concatenation, ConcatenationRepetition
        return Concatenation.new(ConcatenationRepetition(other, 0, 1), self)

    # number*self
    __rmul__.register(int, __mul__.dispatcher.dispatch(int))
    __rmul__.register(float, __mul__.dispatcher.dispatch(float))
    __rmul__.register(ellipsis, __mul__.dispatcher.dispatch(ellipsis))

    # [lb,ub]*self
    __rmul__.register(list, __mul__.dispatcher.dispatch(list))

    # self // other
    @singledispatchmethod
    def __floordiv__(self, other: object) -> Expression:
        from pathex import Shuffle
        return Shuffle.new(self, other)

    # self//number
    @__floordiv__.register(int)
    @__floordiv__.register(float)
    @__floordiv__.register(ellipsis)
    def __(self, number):
        from pathex import ShuffleRepetition
        if number is ...:
            number = inf
        return ShuffleRepetition(self, number, number)

    # other // self
    # number//self
    __rfloordiv__ = __floordiv__

    # self % other
    @singledispatchmethod
    def __mod__(self, other: object) -> Expression:
        from pathex import ConcatenationRepetition, Shuffle
        return Shuffle.new(ConcatenationRepetition(self, 0, 1), other)

    # self%number
    @__mod__.register(int)
    @__mod__.register(float)
    @__mod__.register(ellipsis)
    def __(self, number):
        from pathex import ShuffleRepetition
        if number is ...:
            number = inf
        return ShuffleRepetition(self, 0, number)

    # self%[lb, ub]
    @__mod__.register
    def __(self, bounds: list):
        from pathex import ShuffleRepetition
        return ShuffleRepetition(self, *bounds)

    # other % self
    @singledispatchmethod
    def __rmod__(self, other: object) -> Expression:
        from pathex import ConcatenationRepetition, Shuffle
        return Shuffle.new(ConcatenationRepetition(other, 0, 1), self)

    __rmod__.register(int, __mod__.dispatcher.dispatch(int))
    __rmod__.register(float, __mod__.dispatcher.dispatch(float))
    __rmod__.register(ellipsis, __mod__.dispatcher.dispatch(ellipsis))

    # [lb,ub]%self
    __rmod__.register(list, __mod__.dispatcher.dispatch(list))

    @singledispatchmethod
    def __getitem__(self, key: object) -> Expression:
        raise TypeError('Key schema not supported')
