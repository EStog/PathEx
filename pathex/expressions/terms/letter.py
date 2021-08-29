from .term import Term
from dataclasses import dataclass

@dataclass(frozen=True)
class Letter(Term):
    value: object

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.value})'
