from dataclasses import dataclass

from .expression import Expression


@dataclass(frozen=True)
class Negation(Expression):
    argument: object

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.argument})'

__all__ = ['Negation']
