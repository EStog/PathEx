from .letters_union import LettersUnion

__all__ = ['LettersPossitiveUnion']


class LettersPossitiveUnion(LettersUnion):
    """This class represents an union of letters.

    Because of the presence of the negation operator, it is necessary to consider a set of letters, which negation may be taken as a single entity. This class serve as a representation of a language composed only with letters, that is, a set of unitary length strings. This is usefull to cut the application of the negation operator by simply negating the whole set of letters, because the intersection of the negation of each letter (obtained by appling De Morgan law) does not constitute a reducible expression.
    At the semantic level, an union of letters is the same as a union of expression, where each expression is a letter, but it is preferred to use LettersPossitiveUnion in this case.

    >>> from pathpy import LettersPossitiveUnion as Ls
    >>> exp = Ls('abcd')
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'a', 'b', 'c', 'd'}

    >>> exp = Ls('ab') | Ls('cd')
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'a', 'b', 'c', 'd'}
    """

    def get_one_rest(self):
        it = iter(self.letters)
        one = next(it)
        return one, it

    def as_negative(self):
        from .letters_negative_union import LettersNegativeUnion
        return LettersNegativeUnion(self.letters)
