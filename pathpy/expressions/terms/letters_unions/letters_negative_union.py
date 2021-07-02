from .letters_union import LettersUnion


class LettersNegativeUnion(LettersUnion):
    """This represents the negation of a union of letters.
    That is, semantically, LettersNegativeUnion('abc') = Negation(Union('abc')). This represents an infinite language and for that reason LettersNegativeUnion is used in order to perform symbolic transformations.

    See other expressions classes for examples.
    """

__all__ = ['LettersNegativeUnion']
