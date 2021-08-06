from dataclasses import dataclass

from pathpy.expressions.terms.term import Term


@dataclass(frozen=True)
class NamedWildcard(Term):
    """This class represents a wildcard that has been given an identity.

    It is necessary for the lazy generation of the language but it is
    not necessary in the theoretical model from the semantic point of
    view. The class is inmutable.
    """
    identifier: int

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.identifier})'

    def __str__(self):
        return f'_{self.identifier}'


__all__ = ['NamedWildcard']
