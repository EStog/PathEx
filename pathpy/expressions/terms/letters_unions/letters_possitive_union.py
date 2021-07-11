from .letters_union import LettersUnion


class LettersPossitiveUnion(LettersUnion):
    """This class represents an union of letters.

    Because of the presence of the negation operator, it is necessary to consider a set of letters, which negation may be taken as a single entity. This class serve as a representation of a language composed only with letters, that is, a set of unitary length strings. This is usefull to cut the application of the negation operator by simply negating the whole set of letters, because the intersection of the negation of each letter (obtained by appling De Morgan law) does not constitute a reducible expression.
    At the semantic level, an union of letters is the same as a union of expression, where each expression is a letter, but it is preferred to use LettersPossitiveUnion in this case.

    >>> from pathpy import LettersPossitiveUnion as Ls
    >>> assert Ls('abcd').as_set_of_str() == {'a', 'b', 'c', 'd'}

    >>> assert (Ls('ab') | Ls('cd')).as_set_of_str() == {'a', 'b', 'c', 'd'}
    """


__all__ = ['LettersPossitiveUnion']
