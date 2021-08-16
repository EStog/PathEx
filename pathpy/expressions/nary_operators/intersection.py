from .nary_operator import NAryOperator

__all__ = ['Intersection']


class Intersection(NAryOperator):
    r"""`Intersection` is semantically equivalent to intersection of languages (sets of strings), that is, to see the common strings between the considered languages.

    `Intersection` (`&`) can be expressed recursively in the following manner.

    Let `a` and `b` be letters, `A` and `B` strings, and `E` the empty string.
        `aA & bB = (a & b) + (A & B)`
        `a & b = a`                 if `a == b`
        `a & b = {}`                if `a != b`

    Examples:
        >>> from pathpy.expressions.aliases import *
        >>> from functools import partial

        >>> exp = 'a' + U('xy') & 'a' + U('yz')
        >>> assert exp.get_language() ==  \
        ...     exp.get_generator().get_language() == {'ay'}

        >>> exp = 'a' + U('xy') & 'a' + U('yz') + 'w'
        >>> assert exp.get_language() == \
        ...     exp.get_generator().get_language() == set()
        >>> assert exp.get_language(only_complete_words=False) == \
        ...     exp.get_generator().get_language(only_complete_words=False) == {'ay'}

        >>> exp1 = L('a')*... & C('aaa') | C('aa')
        >>> exp2 = C('aaa') | C('aa') & L('a')*...
        >>> assert exp1.get_language() == \
        ...     exp2.get_language() == \
        ...     exp1.get_generator().get_language() == \
        ...     exp2.get_generator().get_language()

        >>> exp = Ls('abc') + C('xyz') & Ls('axy') + C('xyz')
        >>> assert exp.get_language() == \
        ...     exp.get_generator().get_language() == {'axyz'}

        >>> exp = Ls('axy') + C('xyz') & NLs('abc') + C('xyz')
        >>> assert exp.get_language() == {'xxyz', 'yxyz'}
    """
