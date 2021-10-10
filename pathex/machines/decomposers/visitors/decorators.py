from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from pathex.expressions.nary_operators.concatenation import Concatenation
from pathex.expressions.nary_operators.intersection import Intersection
from pathex.expressions.nary_operators.union import Union
from pathex.expressions.repetitions.repetition import Repetition
from pathex.expressions.terms.empty_word import EMPTY_WORD
from pathex.machines.decomposers.visitors.misc import NOT_EMPTY_WORD_MESSAGE
from pathex.expressions.nary_operators.nary_operator import NAryOperator

from ..decomposer import Branches, Decomposer, DecomposerMatchMismatch

_Decomposer = TypeVar('_Decomposer', bound=Decomposer)
_NAryOperator = TypeVar('_NAryOperator', bound=NAryOperator)

def nary_operator_visitor(visitor: Callable[[_Decomposer, _NAryOperator], Branches]):
    @wraps(visitor)
    def f(decomposer: _Decomposer, exp: _NAryOperator) -> Branches:
        if not exp.args_tail:
            yield from decomposer._transform(exp.args_head)
        else:
            yield from visitor(decomposer, exp)

    return f

def matching_operator_visitor(match_func: Callable[[DecomposerMatchMismatch,
                                                    object, object, object], Branches]):
    @wraps(match_func)
    def f(decomposer: DecomposerMatchMismatch, exp: Intersection) -> Branches:
        for head1, tail1 in decomposer._transform(exp.args_head):
            if head1 is EMPTY_WORD and tail1 is not EMPTY_WORD:
                yield EMPTY_WORD, exp.__class__(tail1, *exp.args_tail)
            else:
                for head2, tail2 in decomposer._transform(exp.__class__(exp.args_tail)):
                    if head2 is EMPTY_WORD and tail2 is not EMPTY_WORD:
                        yield EMPTY_WORD, exp.__class__(Concatenation(head1, tail1), tail2)
                    else:
                        # `aA op bB = (a match b) + (A match B)`
                        tail = EMPTY_WORD if tail1 is tail2 is EMPTY_WORD \
                            else exp.__class__(tail1, tail2)
                        yield from match_func(decomposer, head1, head2, tail)
    return f


_Repetition = TypeVar('_Repetition', bound=Repetition)


def repetition_visitor(func: Callable[[Decomposer, _Repetition], Branches]):
    @wraps(func)
    def f(decomposer: Decomposer, exp: _Repetition) -> Branches:
        assert exp.argument is not EMPTY_WORD, NOT_EMPTY_WORD_MESSAGE

        # a//1 = a
        if exp.lower_bound == exp.upper_bound == 1:
            yield EMPTY_WORD, exp.argument

        # a%n = empty | a%[1,n]
        elif exp.lower_bound == 0:
            yield EMPTY_WORD, Union(EMPTY_WORD, exp.__class__(exp.argument, 1, exp.upper_bound))
        else:
            yield from func(decomposer, exp)

    return f
