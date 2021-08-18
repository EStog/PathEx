from .repetition import Repetition

__all__ = ['ConcatenationRepetition']

class ConcatenationRepetition(Repetition):
    """

    Examples:
        >>> from pathpy.expressions.aliases import *
        >>> from pathpy import EMPTY_WORD

        >>> exp = (L('a')+2)*[1,2]
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'aaaa', 'aa'}

        >>> exp = C('ab')*... & C('ab')*2
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'', 'ab', 'abab'}

        >>> exp = C('ab')*2 & C('ab')*...
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'', 'ab', 'abab'}

        >>> exp1 = (C('ab') | EMPTY_WORD) + 'x'
        >>> exp2 = C('ab') * 'x'
        >>> assert exp1.get_language() == exp2.get_language() == exp1.get_generator().get_language()  == exp2.get_generator().get_language() == {'x', 'abx'}
    """
