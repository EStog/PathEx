from dataclasses import dataclass

from pathex.expressions.expression import Expression
from pathex.expressions.terms.term import Term


@dataclass(frozen=True)
class Letter(Term):
    """Represents a single letter

    This class is just for convenience, to convert any object into a letter

    .. testsetup::

       from pathex import Letter

    >>> assert Letter('a') == Letter('a') == 'a'
    >>> from pathex import Concatenation
    >>> assert Letter('a') not in ('b', Letter('b'))
    >>> assert Letter('a') !=  Concatenation('a')
    >>> assert hash(Letter('a')) == hash('a')
    >>> assert repr('a') == repr(Letter('a'))
    """
    value: object

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        elif not isinstance(other, Expression):
            return self.value == other
        else:
            return False

    def __hash__(self):
        return hash(self.value)

    def __repr__(self) -> str:
        return repr(self.value)
