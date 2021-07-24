from dataclasses import dataclass

from pathpy.expressions.nary_operators.concatenation import Concatenation

__all__ = ['Tag']


@dataclass(frozen=True, init=False)
class Tag(Concatenation):
    enter: object
    exit: object

    def __new__(cls, label):
        enter = object()
        exit = object()
        self = super().__new__(cls, enter, exit)
        object.__setattr__(self, 'enter', enter)
        object.__setattr__(self, 'exit', exit)
        return self
