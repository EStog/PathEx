from dataclasses import dataclass

from .expression import Expression

__all__ = ['Negation']


@dataclass(frozen=True)
class Negation(Expression):
    argument: object

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.argument})'
