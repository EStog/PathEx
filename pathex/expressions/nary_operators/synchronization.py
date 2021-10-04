from pathex.expressions.nary_operators.nary_operator import NAryOperator

__all__ = ['Synchronization']


class Synchronization(NAryOperator):
    """

    .. todo::

       Make the examples simpler and move this examples to unittests.

    Example:

    >>> from pathex.expressions.aliases import *
    >>> from pathex.adts.util import SET_OF_TUPLES
    >>> from pathex.generation.defaults import LANGUAGE_TYPE

    >>> def test(exp1, exp2, language, language_type=LANGUAGE_TYPE):
    ...     assert (exp1 @ exp2).get_language(language_type) == (exp1 @ exp2).get_generator().get_language(language_type) == \
            (exp2 @ exp1).get_language(language_type) == (exp2 @ exp1).get_generator().get_language(language_type) == language

    >>> exp1 = ( 'a' + U('xy') )
    >>> exp2 = ( 'a' + U('yz') )
    >>> test(exp1, exp2, {'axy', 'ayx', 'axz', 'azx', 'ay', 'ayz', 'azy'})

    >>> exp1 = ( 'a' + U('xy') )
    >>> exp2 = ( 'a' + U('yz') + 'w' )
    >>> test(exp1, exp2, {'axyw', 'ayxw', 'axzw', 'azxw', 'ayw', 'ayzw', 'azyw'})

    >>> exp1 = ( _ + U('xy') )
    >>> exp2 = ( 'a' + U('yz') )
    >>> test(exp1, exp2, { 'azx', '-aayx', 'a-azy', 'a-axy', 'axz', '-aaxz', 'ayz', 'a-axz', 'azy', 'axy', '-aaxy', '-aazy', '-aazx', '-aayz', 'a-azx', 'a-ayz', 'a-ayx', 'ay', 'a-ay', '-aay', 'ayx' })

    >>> exp1 = ( _ + U('xy') )
    >>> exp2 = ( 'a' + (_|'z') )
    >>> test(exp1, exp2, {'a-xx', 'ax-x', 'a-azx', 'a-axz', '-aay-y', '-aazx', 'a-a-xx', 'a-ay', '-aax', 'axz', 'a-ax-x', 'a-azy', '-aa-xx', 'a-ax', 'a-yy', '-aay', 'a-a-yy', '-aax-x', '-aa-yy', '-aaxz', 'a-ayz', 'a-ay-y', 'azx', 'ay', 'ax', '-aazy', 'ay-y', '-aayz', 'ayz', 'azy'})

    >>> exp1 = (LC('abc') + C('xyz'))
    >>> exp2 = C('qxyz')
    >>> test(exp1, exp2, {('q', LC('a', 'c', 'q', 'b'), 'x', 'y', 'z'), (LC('a', 'c', 'q', 'b'), 'q', 'x', 'y', 'z'), ('q', 'x', 'y', 'z')}, SET_OF_TUPLES)

    >>> exp1 = (LC('abc') + C('xyz'))
    >>> exp2 = C('axyz')
    >>> test(exp1, exp2, {(LC('b', 'a', 'c'), 'a', 'x', 'y', 'z'), ('a', LC('b', 'a', 'c'), 'x', 'y', 'z')}, SET_OF_TUPLES)

    >>> exp1 = _ + C('abc')
    >>> exp2 = C('wabc')
    >>> test(exp1, exp2, {'wabc', '-wwabc', 'w-wabc'})

    >>> exp1 = _ + C('abc')
    >>> exp2 = LC('w') + C('ab')
    >>> test(exp1, exp2, {'w-wabc', '-wwabc', '-wabc'})

    >>> exp1 = _ + C('abc')
    >>> exp2 = _ + C('ab') + U('cd')
    >>> test(exp1, exp2, {'_abc', '_abcd', '_abdc'})

    >>> exp1 = LC('w') + C('abc')
    >>> exp2 = LC('w') + C('abc')
    >>> test(exp1, exp2, {'-wabc'})

    >>> exp1 = LC('x') + C('abc')
    >>> exp2 = LC('w') + C('abc')
    >>> test(exp1, exp2, {(LC('w'),'w','a','b','c'), (LC('w','x'),'a', 'b', 'c'),
    ...                   (LC('x'), 'x', 'a', 'b', 'c'), ('w', LC('w'), 'a', 'b', 'c'),
    ...                   ('x', LC('x'), 'a', 'b', 'c')},
    ...      SET_OF_TUPLES)
    """
