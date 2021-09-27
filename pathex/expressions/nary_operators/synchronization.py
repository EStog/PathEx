from .nary_operator import NAryOperator

__all__ = ['Synchronization']


class Synchronization(NAryOperator):
    """


    Example:

    >>> from pathex.expressions.aliases import *
    >>> from pathex.adts.util import SET_OF_TUPLES

    >>> exp = ( 'a' + U('xy') ) @ ( 'a' + U('yz') )
    >>> assert exp.get_language() == exp.get_generator().get_language() == {
    ...     'axy', 'ayx', 'axz', 'azx', 'ay', 'ayz', 'azy'}

    >>> exp = ( 'a' + U('xy') ) @ ( 'a' + U('yz') + 'w' )
    >>> assert exp.get_language() == exp.get_generator().get_language() == {
    ...     'axyw', 'ayxw', 'axzw', 'azxw', 'ayw', 'ayzw', 'azyw'}
    """
