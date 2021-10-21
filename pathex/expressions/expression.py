from __future__ import annotations

from abc import ABC
from math import inf
from typing import Collection, Generator, TypeVar

from pathex.adts.collection_wrapper import CollectionWrapper
from pathex.generation.defaults import COMPLETE_WORDS, LANGUAGE_TYPE, WORD_TYPE
from pathex.machines.decomposers.decomposer import Decomposer

__doc__ = f"""

Expressions abstract base class
===============================

:Module: ``{__name__}``

.. sectionauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>
.. codeauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>

---------------------------------------------------------------
"""

# TODO: __str__ y __repr__ de todas las expresiones

# TODO: Refactory operators overloading

__all__ = ['Expression']

ellipsis = type(...)
T = TypeVar('T', bound=CollectionWrapper)
E = TypeVar('E', bound=CollectionWrapper)


def _get_non_optional_repetition_or_binary_op(binary_op):
    def f(self, v):
        import pathex
        if v in (inf, Ellipsis):
            return pathex.__dict__[f'{binary_op}Repetition'](self, 1, inf)
        elif isinstance(v, int):
            return pathex.__dict__[f'{binary_op}Repetition'](self, v, v)
        else:
            return pathex.__dict__[binary_op](self, v)
    return f


def _get_optional_repetition_or_binary_op(binary_op):
    def f(self, v):
        import pathex
        if isinstance(v, list):
            return pathex.__dict__[f'{binary_op}Repetition'](self, *v)
        elif v in (inf, Ellipsis) or isinstance(v, int):
            return pathex.__dict__[f'{binary_op}Repetition'](self, 0, v)
        else:
            from pathex import optional
            return pathex.__dict__[binary_op](optional(self), v)
    return f


class Expression(ABC):
    """Expressions abstract base class.

    In |pe| objects of any other kind different from :class:`Expression` are interpreted as an identity terminal expression. :class:`Expression` is meant to grouping those kind of expressions that has a special meaning and to provide general methods and Python operator overloading.
    """

    def get_generator(self, decomposer: Decomposer | None = None):
        """get_generator(machine: pathex.generation.machines.machine.Machine | None = None) -> pathex.generation.words_generator.WordsGenerator

        Gives a :class:`~.WordsGenerator` with default values for the actual expression.

        This method is meant as a handy shortcut for :class:`WordsGenerator(expression, machine) <.WordsGenerator>`.

        ``machine`` is the machine to be used to interpret the expression. If it is :obj:`None` then an instance of :class:`~.ExtendedMachineCompalphabet` will be used. Defaults to :obj:`None`.
        """
        if decomposer is None:
            from pathex.machines.decomposers.extended_decomposer_compalphabet import \
                ExtendedDecomposerCompalphabet
            decomposer = ExtendedDecomposerCompalphabet()
        from pathex.generation.words_generator import WordsGenerator
        return WordsGenerator(self, decomposer)

    def get_eager_generator(self, decomposer: Decomposer | None = None,
                            complete_words: bool = COMPLETE_WORDS) -> Generator[Collection, None, None]:
        if decomposer is None:
            from pathex.machines.decomposers.extended_decomposer_compalphabet import \
                ExtendedDecomposerCompalphabet
            decomposer = ExtendedDecomposerCompalphabet()
        from pathex.generation.eager import words_generator
        return words_generator(self, decomposer, complete_words)
    get_eager_generator.__doc__ = f"""
        get_eager_generator(self, machine: pathex.generation.machines.machine.Machine | None = None, word_type: type[T] = {WORD_TYPE.__name__}, complete_words: bool = {COMPLETE_WORDS}) -> typing.Generator[T, None, None]

        Gives a generator of :class:`~.CollectionWrapper` object that represent the words generated by the expression.

        This method is meant as a handy shortcut for :func:`words_generator(self, machine, word_type, complete_words) <.words_generator>`.

        ``machine`` is The machine to be used to interpret the expression. If it is :obj:`None` then an instance of :class:`~.ExtendedMachineCompalphabet` will be used. Defaults to :obj:`None`.

        ``word_type`` is a :class:`~.CollectionWrapper` subtype that will be the type of collection to be used to represent words. Defaults to :class:`{WORD_TYPE.__name__} <.CollectionWrapper>`.

        ``complete_words`` is a flag indicating if only complete words are to be given. Defaults to :obj:`{COMPLETE_WORDS}`.
        """

    def get_language(self, language_type: type[T] = LANGUAGE_TYPE,
                     decomposer: Decomposer | None = None,
                     complete_words: bool = COMPLETE_WORDS) -> T:
        if decomposer is None:
            from pathex.machines.decomposers.extended_decomposer_compalphabet import \
                ExtendedDecomposerCompalphabet
            decomposer = ExtendedDecomposerCompalphabet()
        from pathex.generation.eager import words_generator
        language = language_type()
        for w in words_generator(self, decomposer, complete_words):
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
        from pathex import Union
        return Union(self, other)

    # other | self
    def __ror__(self, other):
        from pathex import Union
        return Union(other, self)

    # self & other
    def __and__(self, other):
        from pathex import Intersection
        return Intersection(self, other)

    # other & self
    def __rand__(self, other: object):
        from pathex import Intersection
        return Intersection(other, self)

    # self - other
    def __sub__(self, other):
        from pathex import Difference
        return Difference(self, other)

    # other - self
    def __rsub__(self, other):
        from pathex import Difference
        return Difference(other, self)

    # self+...
    # self+inf
    # self+number
    # self + other
    __add__ = _get_non_optional_repetition_or_binary_op('Concatenation')

    # other + self
    def __radd__(self, v):
        from pathex import Concatenation
        return Concatenation(v, self)

    # +self
    def __pos__(self):
        from pathex import ConcatenationRepetition
        return ConcatenationRepetition(self, 1, inf)

    # self*[lb,ub]
    # self*number
    # self * other
    __mul__ = _get_optional_repetition_or_binary_op('Concatenation')

    # other * self
    def __rmul__(self, v):
        from pathex import Concatenation, optional
        return Concatenation(optional(v), self)

    # self//...
    # self//inf
    # self//number
    # self // other
    __floordiv__ = _get_non_optional_repetition_or_binary_op('Shuffle')

    # other // self
    def __rfloordiv__(self, v):
        from pathex import Shuffle
        return Shuffle(v, self)

    # self%[lb, ub]
    # self%number
    # self % other
    __mod__ = _get_optional_repetition_or_binary_op('Shuffle')

    # other % self
    def __rmod__(self, v):
        from pathex import Shuffle, optional
        return Shuffle(optional(v), self)
