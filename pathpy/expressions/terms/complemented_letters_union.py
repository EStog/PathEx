from typing import Iterable
from .term import Term
from dataclasses import dataclass

@dataclass(frozen=True, repr=False)
class ComplementedLettersUnion(Term):
    letters: set

    def __init__(self, letters: Iterable) -> None:
        object.__setattr__(self, 'letters', set(letters))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.letters!r})'
