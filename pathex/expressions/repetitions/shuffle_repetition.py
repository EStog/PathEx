from pathex.expressions.repetitions.repetition import Repetition

__all__ = ['ShuffleRepetition']


class ShuffleRepetition(Repetition):
    """


    Examples:
        >>> from pathex.expressions.aliases import *

        >>> exp = S('ab')%[1,2]
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'ab', 'ba', 'abab', 'abba', 'baba', 'aabb', 'baab', 'bbaa'}

        >>> exp &= C('ab')%...
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'ab', 'abab', 'aabb'}

        >>> exp = L('a')%[3, 4]
        >>> exp1 = L('a')*[3, 4]
        >>> assert exp.get_language() == exp.get_generator().get_language() == exp1.get_language() == exp1.get_generator().get_language() == {'aaa', 'aaaa'}

        >>> exp = L('a')//1
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'a'}

    """
