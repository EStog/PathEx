from pathex.expressions.repetitions.repetition import Repetition

__all__ = ['ConcatenationRepetition']


class ConcatenationRepetition(Repetition):
    """

    Examples:
        >>> from pathex.expressions.aliases import *
        >>> from pathex.expressions.non_fundamentals import optional

        >>> exp = (L('a')+2)*[1,2]
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'aaaa', 'aa'}

        >>> exp = C('ab')*... & C('ab')*2
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'', 'ab', 'abab'}

        >>> exp = C('ab')*2 & C('ab')*...
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'', 'ab', 'abab'}

        >>> exp1 = optional(C('ab')) + 'x'
        >>> exp2 = C('ab') * 'x'
        >>> assert exp1.get_language() == exp2.get_language() == exp1.get_generator().get_language()  == exp2.get_generator().get_language() == {'x', 'abx'}

        >>> exp = L('a')%[0, 2]
        >>> exp1 = L('a')*[0, 2]
        >>> assert exp.get_language() == exp.get_generator().get_language() == exp1.get_language() == exp1.get_generator().get_language() == {'', 'a', 'aa'}

        >>> exp = L('a')+1
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'a'}
    """
