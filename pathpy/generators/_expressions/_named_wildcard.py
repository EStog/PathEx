from dataclasses import dataclass

from pathpy.expressions.terms.term import Term

@dataclass(frozen=True)
class NamedWildcard(Term):
    """This class represents a wildcard that has been given an identity.

    It is necessary for the lazy generation of the language but it is
    not necessary in the theoretical model from the semantic point of
    view. The class is inmutable.
    """
    name: int

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name})'

    def __str__(self):
        raise TypeError(f'{self.__class__.__name__} can not be represented as str')


__all__ = ['NamedWildcard']
