from __future__ import annotations

from abc import ABC
from functools import singledispatchmethod
from math import inf
from typing import Generator, TypeVar

from pathex.adts.collection_wrapper import CollectionWrapper
from pathex.generation.defaults import COMPLETE_WORDS, LANGUAGE_TYPE, WORD_TYPE
from pathex.generation.machines.machine import Machine

__doc__ = f"""

Expressions abstract base class
===============================

:Module: ``{__name__}``

.. sectionauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>
.. codeauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>

---------------------------------------------------------------
"""

# TODO: __str__ y __repr__ de todas las expresiones

__all__ = ['Expression']

ellipsis = type(...)
T = TypeVar('T', bound=CollectionWrapper)
E = TypeVar('E', bound=CollectionWrapper)


class Expression(ABC):
    """Expressions abstract base class.

    In |pe| objects of any other kind different from :class:`Expression` are interpreted as an identity terminal expression. :class:`Expression` is meant to grouping those kind of expressions that has a special meaning and to provide general methods and Python operator overloading.
    """

    def get_generator(self, machine: Machine | None = None):
        """get_generator(machine: pathex.generation.machines.machine.Machine | None = None) -> pathex.generation.words_generator.WordsGenerator

        Gives a :class:`~.WordsGenerator` with default values for the actual expression.

        This method is meant as a handy shortcut for :class:`WordsGenerator(expression, machine) <.WordsGenerator>`.

        ``machine`` is the machine to be used to interpret the expression. If it is :obj:`None` then an instance of :class:`~.ExtendedMachineCompalphabet` will be used. Defaults to :obj:`None`.
        """
        if machine is None:
            from pathex.generation.machines.extended_machine_compalphabet import \
                ExtendedMachineCompalphabet
            machine = ExtendedMachineCompalphabet()
        from pathex.generation.words_generator import WordsGenerator
        return WordsGenerator(self, machine)

    def get_eager_generator(self, machine: Machine | None = None,
                            word_type: type[T] = WORD_TYPE,
                            complete_words: bool = COMPLETE_WORDS) -> Generator[T, None, None]:
        if machine is None:
            from pathex.generation.machines.extended_machine_compalphabet import \
                ExtendedMachineCompalphabet
            machine = ExtendedMachineCompalphabet()
        from pathex.generation.eager import words_generator
        return words_generator(self, machine, word_type, complete_words)
    get_eager_generator.__doc__ = f"""
        get_eager_generator(self, machine: pathex.generation.machines.machine.Machine | None = None, word_type: type[T] = {WORD_TYPE.__name__}, complete_words: bool = {COMPLETE_WORDS}) -> typing.Generator[T, None, None]

        Gives a generator of :class:`~.CollectionWrapper` object that represent the words generated by the expression.

        This method is meant as a handy shortcut for :func:`words_generator(self, machine, word_type, complete_words) <.words_generator>`.

        ``machine`` is The machine to be used to interpret the expression. If it is :obj:`None` then an instance of :class:`~.ExtendedMachineCompalphabet` will be used. Defaults to :obj:`None`.

        ``word_type`` is a :class:`~.CollectionWrapper` subtype that will be the type of collection to be used to represent words. Defaults to :class:`{WORD_TYPE.__name__} <.CollectionWrapper>`.

        ``complete_words`` is a flag indicating if only complete words are to be given. Defaults to :obj:`{COMPLETE_WORDS}`.
        """

    def get_language(self, language_type: type[T] = LANGUAGE_TYPE,
                     machine: Machine | None = None,
                     word_type: type[CollectionWrapper] = WORD_TYPE,
                     complete_words: bool = COMPLETE_WORDS) -> T:
        if machine is None:
            from pathex.generation.machines.extended_machine_compalphabet import \
                ExtendedMachineCompalphabet
            machine = ExtendedMachineCompalphabet()
        from pathex.generation.eager import words_generator
        language = language_type()
        for w in words_generator(self, machine, word_type, complete_words=complete_words):
            language.put(w)
        return language
    get_language.__doc__ = f"""
        get_language(language_type: type[T] = {LANGUAGE_TYPE.__name__}, machine: pathex.generation.machines.machine.Machine | None = None, word_type: type[pathex.adts.collection_wrapper.CollectionWrapper] = {WORD_TYPE.__name__}, complete_words: bool = {COMPLETE_WORDS}) -> T

        Gives a :class:`~.CollectionWrapper` object that contains :class:`~.CollectionWrapper` objects that represent the words generated by the expression.

        ``language_type`` is a subtype of :class:`~.CollectionWrapper` that will be used as the type of the object to be returned. Defaults to :class:`{LANGUAGE_TYPE.__name__} <.CollectionWrapper>`.

        ``machine`` is the machine to be used to interpret the expression. If it is :obj:`None` then an instance of :class:`~.ExtendedMachineCompalphabet` will be used. Defaults to :obj:`None`.

        ``word_type`` is a :class:`~.CollectionWrapper` subtype that will be the type of collection to be used to represent words. Defaults to :class:`{WORD_TYPE.__name__} <.CollectionWrapper>`.

        ``complete_words`` is a flag indicating if only complete words are to be given. Defaults to :obj:`{COMPLETE_WORDS}`.
        """

    # self | other
    def __or__(self, other):
        """__or__(other: object) -> pathex.expressions.nary_operators.union.Union

        Vertical bar symbol (``|``) is used to construct :class:`~.Union` expression instances:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Union

        >>> assert L('a') | 'b' == Union(L('a'), 'b')

        :class:`~.Union` arguments are always given in a flattened manner when constructed with ``|``:

        >>> assert L('a') | 'b' | 'c' == Union(L('a'), 'b', 'c')
        """
        from pathex import Union
        return Union.flattened(self, other)

    # other | self
    def __ror__(self, other):
        """__ror__(other: object) -> pathex.expressions.nary_operators.union.Union

        Although :class:`~.Union` is conmutative this construction (reflected ``|`` operator) preserve the order of the operands to allow the user to change the order of evaluation:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Union

        >>> exp1 = L('a') | 'b'
        >>> exp2 = 'b' | L('a')
        >>> assert exp1 != exp2
        >>> assert exp1 == Union(L('a'), 'b')
        >>> assert exp2 == Union('b', L('a'))

        However, the semantics remain the same:

        >>> assert exp1.get_language() == exp2.get_language() == {'a', 'b'}
        """
        from pathex import Union
        return Union.flattened(other, self)

    # self & other
    def __and__(self, other):
        """__and__(other: object) -> pathex.expressions.nary_operators.intersection.Intersection

        Ampersand symbol (``&``) is used to construct :class:`~.Intersection` expression instances:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Intersection

        >>> assert L('a') & 'a' == Intersection(L('a'), 'a')

        :class:`~.Intersection` arguments are always given in a flattened manner when constructed with ``&``:

        >>> assert L('a') & 'a' & 'b' == Intersection(L('a'), 'a', 'b')
        """
        from pathex import Intersection
        return Intersection.flattened(self, other)

    # other & self
    def __rand__(self, other: object):
        """__rand__(other: object) -> pathex.expressions.nary_operators.intersection.Intersection

        Although :class:`~.Intersection` is conmutative this construction (reflected ``&`` operator) preserve the order of the operands to allow the user to change the order of evaluation:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Intersection

        >>> exp1 = L('a') & 'a'
        >>> exp2 = 'a' & L('a')
        >>> assert exp1 != exp2
        >>> assert exp1 == Intersection(L('a'), 'a')
        >>> assert exp2 == Intersection('a', L('a'))

        However, the semantics remain the same:

        >>> assert exp1.get_language() == exp2.get_language() == {'a'}
        """
        from pathex import Intersection
        return Intersection.flattened(other, self)

    # self @ other
    def __matmul__(self, other):
        """__matmul__(self, other: object) -> pathex.expressions.nary_operators.synchronization.Synchronization

        Arroba symbol (``@``) is used to construct :class:`~.Synchronization` expression instances:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Synchronization

        >>> assert L('a') @ 'a' == Synchronization(L('a'), 'a')

        :class:`~.Synchronization` arguments are always given in a flattened manner when constructed with ``@``:

        >>> assert L('a') @ 'a' @ 'b' == Synchronization(L('a'), 'a', 'b')
        """
        from pathex import Synchronization
        return Synchronization.flattened(self, other)

    # other @ self
    def __rmatmul__(self, other):
        """__rmatmul__(other: object) -> pathex.expressions.nary_operators.synchronization.Synchronization

        Although :class:`~.Synchronization` is conmutative this construction (reflected ``@`` operator) preserve the order of the operands to allow the user to change the order of evaluation:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Synchronization

        >>> exp1 = L('a') @ 'b'
        >>> exp2 = 'b' @ L('a')
        >>> assert exp1 != exp2
        >>> assert exp1 == Synchronization(L('a'), 'b')
        >>> assert exp2 == Synchronization('b', L('a'))

        However, the semantics remain the same:

        >>> assert exp1.get_language() == exp2.get_language() == {'ab', 'ba'}
        """
        from pathex import Synchronization
        return Synchronization.flattened(other, self)

    # self - other
    def __sub__(self, other):
        """__sub__(self, other: object) -> pathex.expressions.nary_operators.difference.Difference

        Minus symbol (``-``) is used to construct :class:`~.Difference` expression instances:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Difference

        >>> assert L('a') - 'a' == Difference(L('a'), 'a')
        """
        from pathex import Difference
        return Difference(self, other)

    # other - self
    def __rsub__(self, other):
        """__rsub__(self, other: object) -> pathex.expressions.nary_operators.difference.Difference

        :class:`~.Difference` is not conmutative in general, so reflected ``-`` operator preserve the order of operator:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Difference

        >>> exp1 = L('a') - 'b'
        >>> exp2 = 'b' - L('a')
        >>> assert exp1 != exp2
        >>> assert exp1 == Difference(L('a'), 'b')
        >>> assert exp2 == Difference('b', L('a'))
        """
        from pathex import Difference
        return Difference(other, self)

    # self+...
    # self+inf
    # self+number
    # self + other
    def __add__(self, v: object):
        """__add__(other: object) -> pathex.expressions.nary_operators.concatenation.Concatenation
        __add__(number: int) -> pathex.expressions.repetitions.concatenation_repetition.ConcatenationRepetition

        Plus symbol (``+``) is used to construct :class:`~.Concatenation` and :class:`~.ConcatenationRepetition` expression instances.

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Concatenation, ConcatenationRepetition
            >>> from math import inf

        With :obj:`math.inf`, :data:`Ellipsis` or an :class:`int` as operand a :class:`~.ConcatenationRepetition` is constructed:

        >>> assert L('a')+inf == L('a')+... == ConcatenationRepetition(L('a'), 1, inf)
        >>> assert L('a')+4 == ConcatenationRepetition(L('a'), 4, 4)

        With any other object as operand a :class:`~.Concatenation` is constructed:

        >>> assert L('a') + 'e' == Concatenation(L('a'), 'e')

        :class:`~.Concatenation` arguments are always given in a flattened manner when constructed with ``+``:

        >>> assert L('a') + 'b' + 'c' + 'd' == Concatenation(L('a'), *'bcd')
        """
        if v in (inf, Ellipsis):
            from pathex import ConcatenationRepetition
            return ConcatenationRepetition(self, 1, inf)
        elif isinstance(v, int):
            from pathex import ConcatenationRepetition
            return ConcatenationRepetition(self, v, v)
        else:
            from pathex import Concatenation
            return Concatenation.flattened(self, v)

    # number+self
    # other + self
    def __radd__(self, v):
        """__radd__(other: object) -> pathex.expressions.nary_operators.concatenation.Concatenation
        __radd__(number: int) -> pathex.expressions.repetitions.concatenation_repetition.ConcatenationRepetition

        This is the same as :meth:`__add__` except when it is used to construct :class:`~.Concatenation` because it is not commutative:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Concatenation

        >>> exp1 = L('a') + 's'
        >>> exp2 = 's' + L('a')
        >>> assert exp1 != exp2
        >>> assert exp1 == Concatenation(L('a'), 's')
        >>> assert exp2 == Concatenation('s', L('a'))
        """
        if v in (inf, Ellipsis) or isinstance(v, int):
            return self.__add__(v)
        else:
            from pathex import Concatenation
            return Concatenation.flattened(v, self)

    # +self
    def __pos__(self):
        """__pos__() -> pathex.expressions.repetitions.concatenation_repetition.ConcatenationRepetition:

        Plus symbol (``+``) used as an unary operator constructs a :class:`~.ConcatenationRepetition` expression instance with lower bound ``1`` and upper bound :obj:`math.inf`:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import ConcatenationRepetition
            >>> from math import inf

        >>> assert +L('a') == ConcatenationRepetition(L('a'), 1, inf)
        """
        from pathex import ConcatenationRepetition
        return ConcatenationRepetition(self, 1, inf)

    # self*[lb,ub]
    # self*number
    # self * other
    def __mul__(self, v):
        """__mul__(other: object) -> pathex.expressions.nary_operators.concatenation.Concatenation
        __mul__(bound: [int, int] | int | math.inf | Ellipsis) -> pathex.expressions.repetitions.concatenation_repetition.ConcatenationRepetition

        Asterisk symbol (``*``) is used to construct an optional :class:`~.Concatenation` and :class:`~.ConcatenationRepetition` expressions instances.

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Concatenation, ConcatenationRepetition
            >>> from math import inf

        With any of a :class:`list` of two :class:`int`, an :class:`int`, :obj:`math.inf` or :data:`Ellipsis` as operand it constructs a :class:`~.ConcatenationRepetition`:

        >>> assert L('a')*[2,5] == ConcatenationRepetition(L('a'), 2, 5)
        >>> assert L('a')*4 == L('a')*[0,4] == ConcatenationRepetition(L('a'), 0, 4)
        >>> assert L('a')*inf == L('a')*... == ConcatenationRepetition(L('a'), 0, inf)

        With any other object as operand it constructs an optional :class:`~.Concatenation`:

        >>> assert L('a') * 'e' == Concatenation(ConcatenationRepetition(L('a'), 0, 1), 'e')
        """
        if isinstance(v, list):
            from pathex import ConcatenationRepetition
            return ConcatenationRepetition(self, *v)
        elif v in (inf, Ellipsis) or isinstance(v, int):
            from pathex import ConcatenationRepetition
            return ConcatenationRepetition(self, 0, v)
        else:
            from pathex import Concatenation, ConcatenationRepetition
            return Concatenation.flattened(ConcatenationRepetition(self, 0, 1), v)

    # other * self
    # number*self
    # [lb,ub]*self
    def __rmul__(self, v):
        """__rmul__(other: object) -> pathex.expressions.nary_operators.concatenation.Concatenation
        __rmul__(bound: [int, int] | int | math.inf | Ellipsis) -> pathex.expressions.repetitions.concatenation_repetition.ConcatenationRepetition

        This is the same as :meth:`__mul__` except when it is used to construct :class:`~.Concatenation`:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Concatenation, ConcatenationRepetition

        >>> exp1 = L('a') * 's'
        >>> exp2 = 's' * L('a')
        >>> assert exp1 != exp2
        >>> assert exp1 == Concatenation(ConcatenationRepetition(L('a'), 0, 1), 's')
        >>> assert exp2 == Concatenation(ConcatenationRepetition('s', 0, 1), L('a'))
        """
        if v in (inf, Ellipsis) or isinstance(v, (list, int)):
            return self.__mul__(v)
        else:
            from pathex import Concatenation, ConcatenationRepetition
            return Concatenation.flattened(ConcatenationRepetition(v, 0, 1), self)

    # self//...
    # self//inf
    # self//number
    # self // other
    def __floordiv__(self, v):
        """__floordiv__(other: object) -> pathex.expressions.nary_operators.shuffle.Shuffle
        __floordiv__(other: int) -> pathex.expressions.nary_operators.shuffle_repetition.ShuffleRepetition

        Double slash symbol (``//``) is used to construct :class:`~.Shuffle` and :class:`~.ShuffleRepetition` expression instances.

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Shuffle, ShuffleRepetition
            >>> from math import inf

        With :obj:`math.inf`, :data:`Ellipsis` or an :class:`int` as operand a :class:`~.ShuffleRepetition` is constructed:

        >>> assert L('a')//inf == L('a')//... == ShuffleRepetition(L('a'), 1, inf)
        >>> assert L('a')//4 == ShuffleRepetition(L('a'), 4, 4)

        With any other object as operand a :class:`~.Shuffle` is constructed:

        >>> assert L('a') // 'e' == Shuffle(L('a'), 'e')

        :class:`~.Shuffle` arguments are always given in a flattened manner when constructed with ``+``:

        >>> assert L('a') // 'b' // 'c' // 'd' == Shuffle(L('a'), *'bcd')

        """
        if v in (inf, Ellipsis):
            from pathex import ShuffleRepetition
            return ShuffleRepetition(self, 1, inf)
        elif isinstance(v, int):
            from pathex import ShuffleRepetition
            return ShuffleRepetition(self, v, v)
        else:
            from pathex import Shuffle
            return Shuffle.flattened(self, v)

    # other // self
    # number//self
    def __rfloordiv__(self, v):
        """__rfloordiv__(other: object) -> pathex.expressions.nary_operators.shuffle.Shuffle
        __rfloordiv__(other: int) -> pathex.expressions.nary_operators.shuffle_repetition.ShuffleRepetition

        This is the same as :meth:`__floordiv__` except when it is used to construct :class:`~.Shuffle` because, although that operation is conmutative, this construction (reflected ``//`` operator) preserve the order of the operands to allow the user to change the order of evaluation:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Shuffle

        >>> exp1 = L('a') // 's'
        >>> exp2 = 's' // L('a')
        >>> assert exp1 != exp2
        >>> assert exp1 == Shuffle(L('a'), 's')
        >>> assert exp2 == Shuffle('s', L('a'))

        However, the semantics remain the same:

        >>> assert exp1.get_language() == exp2.get_language() == {'sa', 'as'}
        """
        if v in (inf, Ellipsis) or isinstance(v, int):
            return self.__floordiv__(v)
        else:
            from pathex import Shuffle
            return Shuffle.flattened(v, self)

    # self%[lb, ub]
    # self%number
    # self % other
    def __mod__(self, v):
        """__mod__(other: object) -> pathex.expressions.nary_operators.concatenation.Concatenation
        __mul__(bound: [int, int] | int | math.inf | Ellipsis) -> pathex.expressions.repetitions.shuffle_repetition.ShuffleRepetition

        Asterisk symbol (``%``) is used to construct an optional :class:`~.Shuffle` and :class:`~.ShuffleRepetition` expressions instances.

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Shuffle, ShuffleRepetition, ConcatenationRepetition
            >>> from math import inf

        With any of a :class:`list` of two :class:`int`, an :class:`int`, :obj:`math.inf` or :data:`Ellipsis` as operand it constructs a :class:`~.ShuffleRepetition`:

        >>> assert L('a')%[2,5] == ShuffleRepetition(L('a'), 2, 5)
        >>> assert L('a')%4 == L('a')%[0,4] == ShuffleRepetition(L('a'), 0, 4)
        >>> assert L('a')%inf == L('a')%... == ShuffleRepetition(L('a'), 0, inf)

        With any other object as operand it constructs an optional :class:`~.Shuffle`:

        >>> assert L('a') % 'e' == Shuffle(ConcatenationRepetition(L('a'), 0, 1), 'e')
        """
        if isinstance(v, list):
            from pathex import ShuffleRepetition
            return ShuffleRepetition(self, *v)
        elif v in (inf, Ellipsis) or isinstance(v, int):
            from pathex import ShuffleRepetition
            return ShuffleRepetition(self, 0, v)
        else:
            from pathex import ConcatenationRepetition, Shuffle
            return Shuffle.flattened(ConcatenationRepetition(self, 0, 1), v)

    # [lb, ub]%self
    # number%self
    # other % self
    def __rmod__(self, v):
        """__rmod__(other: object) -> pathex.expressions.nary_operators.shuffle.Shuffle
        __rmod__(bound: [int, int] | int | math.inf | Ellipsis) -> pathex.expressions.repetitions.shuffle_repetition.ShuffleRepetition

        This is the same as :meth:`__mod__` except when it is used to construct :class:`~.Shuffle`. In this case the first argument must allways be an :class:`Expression` instance to avoid confusion with :ref:`old-string-formatting`:

        .. testsetup:: *

            >>> from pathex.expressions.aliases import *
            >>> from pathex import Shuffle, ConcatenationRepetition

        >>> exp1 = L('a') % 's'
        >>> exp2 = L('s') % 'a' # 's' % L('a') means print-style format operation, not Shuffle.
        >>> assert exp1 != exp2
        >>> assert exp1 == Shuffle(ConcatenationRepetition(L('a'), 0, 1), 's')
        >>> assert exp2 == Shuffle(ConcatenationRepetition(L('s'), 0, 1), 'a')
        """
        if v in (inf, Ellipsis) or isinstance(v, (list, int)):
            return self.__mod__(v)
        else:
            from pathex import ConcatenationRepetition, Shuffle
            return Shuffle.flattened(ConcatenationRepetition(v, 0, 1), self)

    @singledispatchmethod
    def __getitem__(self, key: object) -> Expression:
        raise TypeError('Key schema not supported')
