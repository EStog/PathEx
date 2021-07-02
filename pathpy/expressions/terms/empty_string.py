from pathpy.adts.singleton import singleton

from .term import Term


@singleton
class EmptyString(Term):
    """This is a singleton class that represents the
    expression that generates the empty string.
    """
    __slots__ = ()

    def __str__(self):
        return ''


EMPTY_STRING = EmptyString()

__all__ = ['EmptyString', 'EMPTY_STRING']
