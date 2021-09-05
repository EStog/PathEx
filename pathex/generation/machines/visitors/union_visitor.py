from pathex.expressions.nary_operators.union import Union

from ..machine import Branches, Machine

__all__ = ['union_visitor']


def union_visitor(machine: Machine, exp: Union) -> Branches:
    for e in exp:
        yield from machine.branches(e)
