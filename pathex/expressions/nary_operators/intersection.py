from .nary_operator import NAryOperator

__all__ = ['Intersection']


class Intersection(NAryOperator):
    r"""

    Examples:
        >>> from pathex.expressions.aliases import *
        >>> from functools import partial

        >>> exp = 'a' + U('xy') & 'a' + U('yz')
        >>> assert exp.get_language() ==  \
        ...     exp.get_generator().get_language() == {'ay'}

        >>> exp = 'a' + U('xy') & 'a' + U('yz') + 'w'
        >>> assert exp.get_language() == \
        ...     exp.get_generator().get_language() == set()
        >>> assert exp.get_language(complete_words=False) == \
        ...     exp.get_generator().get_language(complete_words=False) == {'ay'}

        >>> exp1 = L('a')*... & C('aaa') | C('aa')
        >>> exp2 = C('aaa') | C('aa') & L('a')*...
        >>> assert exp1.get_language() == \
        ...     exp2.get_language() == \
        ...     exp1.get_generator().get_language() == \
        ...     exp2.get_generator().get_language()

        >>> exp = U('abc') + C('xyz') & U('axy') + C('xyz')
        >>> assert exp.get_language() == \
        ...     exp.get_generator().get_language() == {'axyz'}

        # >>> exp = Ls('axy') + C('xyz') & NLs('abc') + C('xyz')
        # >>> assert exp.get_language() == {'xxyz', 'yxyz'}
    """
