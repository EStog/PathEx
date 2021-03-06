from pathex.adts.singleton import singleton
from pathex.expressions.terms.term import Term


@singleton
class Alphabet(Term):
    """This class represents the language of singleton words, that is, the set of all words of length 1.

    >>> from pathex.expressions.aliases import *
    >>> exp = C(_, *'aby') & C(*'xab', _)
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'xaby'}
    >>> exp = C(_, *'aby') - C(*'xabz')
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'xaby', '-xaby'}
    """

    def __str__(self) -> str:
        return '_'


ALPHABET = Alphabet()
