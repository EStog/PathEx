from .nary_operator import NAryOperator


class Intersection(NAryOperator):
    """`Intersection` is semantically equivalent to intersection of languages (sets of strings), that is, to see the common strings between the considered languages.

    `Intersection` (`&`) can be expressed recursively in the following manner.

    Let `a` and `b` be letters, `A` and `B` strings, and `E` the empty string.
        `aA & bB = (a & b) + (A & B)`
        `a & b = a`                 if `a == b`
        `a & b = {}`                if `a != b`

    Example:
        >>> from pathpy import Union as U, LettersPossitiveUnion as L, Concatenation as C, LettersNegativeUnion as NL
        >>> from pathpy.generators.word_generator import WordGenerator
        >>> from functools import partial

        >>> exp = 'a' + U('xy') & 'a' + U('yz')
        >>> assert exp.as_(set) == {'ay'}

        >>> exp = 'a' + U('xy') & 'a' + U('yz') + 'w'
        >>> assert exp.as_(set) == set()
        >>> assert exp.as_(set, word_reifier=partial(WordGenerator.as_, complete=False)) == {'ay'}

        >>> exp1 = L('a')*... & C('aaa') | C('aa')
        >>> exp2 = C('aaa') | C('aa') & L('a')*...
        >>> assert exp1.as_(set) == exp2.as_(set)

        >>> exp1 = L('abc') + C('xyz')
        >>> exp2 = L('axy') + C('xyz')
        >>> assert (exp1 & exp2).as_(set) == {'axyz'}

        >>> exp1 = NL('abc') + C('xyz')
        >>> exp2 = L('axy') + C('xyz')
        >>> assert (exp1 & exp2).as_(set) == {'xxyz', 'yxyz'}

    """

__all__ = ['Intersection']
