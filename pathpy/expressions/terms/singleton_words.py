from pathpy.adts.singleton import singleton

from .term import Term


@singleton
class SingletonWords(Term):
    """This class represents the language of singleton words, that is, the set of all words of length 1.

    >>> from pathpy.expressions.aliases import *
    >>> exp = C(_, *'aby') & C(*'xab', _)
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'xaby'}
    >>> exp = C(_, *'aby') - C(*'xabz')
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'xaby', '-xaby'}
    """

    def __str__(self) -> str:
        return '_'


SINGLETON_WORDS = SingletonWords()
