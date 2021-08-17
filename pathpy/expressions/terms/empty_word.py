from pathpy.adts.singleton import singleton

from .term import Term

__all__ = ['EmptyWord', 'EMPTY_WORD']


@singleton
class EmptyWord(Term):
    """This is a singleton class that represents the
    expression that generates the empty string.
    """
    __slots__ = ()

    def __str__(self):
        return ''


EMPTY_WORD = EmptyWord()
