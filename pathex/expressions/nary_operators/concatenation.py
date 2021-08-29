from .nary_operator import NAryOperator

__all__ = ['Concatenation']


class Concatenation(NAryOperator):
   """

   Examples:
      >>> from pathex import Union as U, Concatenation as C, Intersection as I, EMPTY_WORD

      >>> exp = U('ab') + C('xy')
      >>> assert exp.get_language() == exp.get_generator().get_language() == {'axy', 'bxy'}

      >>> exp = 'a' + I('xy')
      >>> assert exp.get_language() == exp.get_generator().get_language() == set()

      >>> exp = I('xy') + 'a'
      >>> assert exp.get_language() == exp.get_generator().get_language() == set()

      >>> assert EMPTY_WORD.get_language() == EMPTY_WORD.get_generator().get_language() == {''}
    """
