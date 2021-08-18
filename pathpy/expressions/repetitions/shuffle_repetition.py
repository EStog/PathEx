from .repetition import Repetition

__all__ = ['ShuffleRepetition']


class ShuffleRepetition(Repetition):
    """
    

    Examples:
        >>> from pathpy import Shuffle as S, Concatenation as C

        >>> exp = S('ab')%[1,2]
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'ab', 'ba', 'abab', 'abba', 'baba', 'aabb', 'baab', 'bbaa'}

        >>> exp &= C('ab')%...
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'ab', 'abab', 'aabb'}
    """
