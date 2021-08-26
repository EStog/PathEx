from .nary_operator import NAryOperator

__all__ = ['Difference']


class Difference(NAryOperator):
    """
    >>> from pathpy.expressions.aliases import *

    >>> exp = ( U('ab') + U('xy') ) - ( U('abxy') + U('abxy') )
    >>> assert exp.get_language() == exp.get_generator().get_language() == set()
    >>> exp = ( U('xab') + U('xy') ) - ( U('ab') + U('ab') )
    >>> assert exp.get_language() == exp.get_generator().get_language() == \
        {'ax', 'ay', 'bx', 'by', 'xx', 'xy'}
    >>> exp = L('a') - L('b')
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'a'}
    >>> exp = L('a') - L('a')
    >>> assert exp.get_language() == exp.get_generator().get_language() == set()
    """
