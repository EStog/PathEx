from pathex.adts.singleton import singleton
from pathex.expressions.terms.term import Term

__all__ = ['EmptyWord', 'EMPTY_WORD']


@singleton
class EmptyWord(Term):
    """This is a singleton class that represents the
    expression that generates the empty string.

    The string representation of the empty word is the empty string:

    .. testsetup::

       from pathex import EMPTY_WORD

    >>> assert str(EMPTY_WORD) == ''
    """
    __slots__ = ()

    def __str__(self):
        return ''


EMPTY_WORD = EmptyWord()
