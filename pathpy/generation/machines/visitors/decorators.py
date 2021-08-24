from functools import wraps
from typing import Callable, TypeVar

from pathpy.expressions.nary_operators.nary_operator import NAryOperator

from ..machine import Branches, Machine

_E = TypeVar('_E', bound=NAryOperator)
_M = TypeVar('_M', bound=Machine)


def nary_operator_visitor(func: Callable[[_M, _E], Branches]):
    @wraps(func)
    def f(machine: _M, exp: _E) -> Branches:
        if exp.head is not None:
            if exp.tail.head is None:
                yield from machine.branches(exp.head)
                return

        yield from func(machine, exp)
    return f
