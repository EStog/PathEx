from .nary_operator import NAryOperator

__all__ = ['Difference']


class Difference(NAryOperator):
    """
    >>> from pathex.expressions.aliases import *

    >>> exp = ( U('ab') + U('xy') ) - ( U('abxy') + U('abxy') )
    >>> assert exp.get_language() == exp.get_generator().get_language() == set()
    >>> exp = ( U('xab') + U('xy') ) - ( U('ab') + U('ab') )
    >>> assert exp.get_language() == exp.get_generator().get_language() == \
        {'ax', 'ay', 'bx', 'by', 'xx', 'xy'}
    >>> exp = L('a') - L('b')
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'a'}
    >>> exp = L('a') - L('a')
    >>> assert exp.get_language() == exp.get_generator().get_language() == set()
    >>> exp = C('ab') - 'abc'
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'ab'}

    In the case of the presence of :class:`SingletonWords` object the difference may be given in a decomposed manner.

    >>> exp = _+3 - C('ab')
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'-ab_', 'ab_', 'a-b_', '-a-b_'} # this is the same as {'___'}, but this is given descomposed.
    """
