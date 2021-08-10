from pathpy.adts.singleton import singleton

from .term import Term

__all__ = ['Wildcard', 'WILDCARD']


@singleton
class Wildcard(Term):
    __slots__ = ()

    def __str__(self) -> str:
        return '_'


WILDCARD = Wildcard()
