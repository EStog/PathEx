from ..machine import Branches, Machine
from pathex.expressions.nary_operators.union import Union

__all__ = ['union_visitor']


def union_visitor(machine: Machine, exp: Union, *extra) -> Branches:
    for e in exp:
        yield from machine.branches(e, *extra)
