from dataclasses import dataclass

from ..term import Term

__all__ = ['LettersUnion']


@dataclass(frozen=True)
class LettersUnion(Term):
    letters: frozenset[object]

    def __init__(self, *letters):
        if len(letters) == 1:
            letters = letters[0]
        letters = frozenset(letters)
        assert letters, '`letters` must not be empty'
        object.__setattr__(self, 'letters', letters)

    @property
    def iterable(self):
        return self.letters

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({set(self.letters)!r})'
