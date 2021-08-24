from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from pathpy.expressions.nary_operators.nary_operator import NAryOperator
from pathpy.expressions.terms.empty_word import EMPTY_WORD

from ..machine import Branches, Machine

_NAry = TypeVar('_NAry', bound=NAryOperator)
_Machine = TypeVar('_Machine', bound=Machine)


def nary_operator_visitor(visitor: Callable[[_Machine, _NAry], Branches]):
    @wraps(visitor)
    def f(machine: _Machine, exp: _NAry) -> Branches:
        if exp.head is not None:
            if exp.tail.head is None:
                yield from machine.branches(exp.head)
                return

        yield from visitor(machine, exp)

    return f


def matching_operator_visitor(match_func: Callable[[_Machine, object, object, object], Branches]):
    @wraps(match_func)
    def f(machine: _Machine, exp: NAryOperator) -> Branches:
        for head1, tail1 in machine.branches(exp.head):
            for head2, tail2 in machine.branches(exp.tail):
                # `aA op bB = (a match b) + (A match B)`
                tail = EMPTY_WORD if tail1 is tail2 is EMPTY_WORD \
                    else exp.__class__(tail1, tail2)

                yield from match_func(machine, head1, head2, tail)

    return f
