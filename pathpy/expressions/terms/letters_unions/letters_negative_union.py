from .letters_union import LettersUnion


class LettersNegativeUnion(LettersUnion):
    """This represents the negation of a union of letters.
    That is, semantically, LettersNegativeUnion('abc') = Negation(Union('abc')). This represents an infinite language and for that reason LettersNegativeUnion is used in order to perform symbolic transformations.

    See other expressions classes for examples.
    """
    def as_possitive(self):
        from .letters_possitive_union import LettersPossitiveUnion
        return LettersPossitiveUnion(self.letters)

    def __str__(self):
        s = ''.join(f'{x}|' for x in self.letters)
        return f'-({s[:-1]})' if len(self.letters) > 1 else f'-{s[:-1]}'

__all__ = ['LettersNegativeUnion']
