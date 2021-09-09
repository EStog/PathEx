from .nary_operator import NAryOperator

__all__ = ['Concatenation']


class Concatenation(NAryOperator):
    """
    Examples:
       >>> from pathex.expressions.aliases import *

       >>> exp = U('ab') + C('xy')
       >>> assert exp.get_language() == exp.get_generator().get_language() == {'axy', 'bxy'}

       >>> exp = 'a' + I('xy')
       >>> assert exp.get_language() == exp.get_generator().get_language() == set()

       >>> exp = I('xy') + 'a'
       >>> assert exp.get_language() == exp.get_generator().get_language() == set()

       >>> assert E.get_language() == E.get_generator().get_language() == {''}
     """
