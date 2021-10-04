from dataclasses import dataclass
from pathex.expressions.terms.term import Term


@dataclass(frozen=True)
class LettersComplement(Term):
    """This class represents the complement of a language of singleton words (words of length 1).

    >>> from pathex.expressions.aliases import *
    >>> exp = ( LC('a')+'a' ) & ( C('ab')|C('ba')|C('aa')|C('xa') )
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'ba', 'xa'}
    >>> assert str(LC('abc')) in {'-(a|b|c)', '-(a|c|b)', '-(b|a|c)', '-(b|c|a)', '-(c|a|b)', '-(c|b|a)'}
    """
    letters: frozenset

    def __init__(self, *letters) -> None:
        if len(letters) == 1:
            letters = next(iter(letters))
        object.__setattr__(self, 'letters', frozenset(letters))

    def __repr__(self) -> str: # pragma: no cover
        t = str(tuple(self.letters)) if len(self.letters) > 1 \
            else str(tuple(self.letters))[:-2]+')'
        return f'{self.__class__.__name__}{t}'

    def __str__(self) -> str:
        t = ''
        for x in self.letters:
            t += f'{str(x)}|'
        t = t[:-1]
        if len(self.letters) > 1:
            t = f'({t})'
        return f'-{t}'
