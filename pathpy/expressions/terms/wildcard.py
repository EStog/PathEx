from pathpy.adts.singleton import singleton

from .term import Term


@singleton
class Wildcard(Term):
    __slots__ = ()

    def __str__(self) -> str:
        raise TypeError(f'{self.__class__.__name__} can not be represented as str')


WILDCARD = Wildcard()


__all__ = ['Wildcard', 'WILDCARD']
