from .nary_operator import NAryOperator

__all__ = ['Shuffle']


class Shuffle(NAryOperator):
    """

    Example:
        >>> from pathpy import Concatenation as C, Shuffle as S

        >>> exp = S('ab')
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'ab', 'ba'}

        >>> exp = S('aa')
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'aa'}

        >>> exp = C('abc') // C('xy')
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'abcxy', 'abxcy', 'abxyc', 'axbcy', 'axbyc', 'axybc', 'xabcy', 'xabyc', 'xaybc', 'xyabc'}
    """
