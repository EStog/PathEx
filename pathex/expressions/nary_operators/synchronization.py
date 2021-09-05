from pathex.adts.util import flattened

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

        # >>> exp = ( _ + U('xy') ) @ ( 'a' + U('yz') )
        # >>> assert exp.get_language() == exp.get_generator().get_language() == { 'azx', '-aayx', 'a-azy', 'a-axy', 'axz', '-aaxz', 'ayz', 'a-axz', 'azy', 'axy', '-aaxy', '-aazy', '-aazx', '-aayz', 'a-azx', 'a-ayz', 'a-ayx', 'ay', 'a-ay', '-aay', 'ayx' }

        # >>> exp = ( _ + U('xy') ) @ ( 'a' + (_|'z') )
        # >>> assert exp.get_language() == exp.get_generator().get_language() == {'a-xx', 'ax-x', 'a-azx', 'a-axz', '-aay-y', '-aazx', 'a-a-xx', 'a-ay', '-aax', 'axz', 'a-ax-x', 'a-azy', '-aa-xx', 'a-ax', 'a-yy', '-aay', 'a-a-yy', '-aax-x', '-aa-yy', '-aaxz', 'a-ayz', 'a-ay-y', 'azx', 'ay', 'ax', '-aazy', 'ay-y', '-aayz', 'ayz', 'azy'}

        # >>> exp = C('xabx')['x':_] @ ( C('a', _, _, 'a') | C(*'bab', _) )
        # >>> assert exp.get_language() == exp.get_generator().get_language() == {'a-aab-ba', 'aa-aba', 'a-aaba', 'aab-ba', 'aaba', 'aa-bba', 'babb', 'bab-bb', 'aa-a-bba', 'a-aa-bba', 'aa-ab-ba', 'babb-b'}

        # >>> exp = C('xab')['x':_] @ C('yby')['y':_]
        # >>> assert exp.get_language() == exp.get_generator().get_language() == {'babb', 'bbab'}

        # >>> exp = (NLs('abc') + C('xyz')) @ C('qxyz')
        # >>> assert exp.get_language(SET_OF_TUPLES) == exp.get_generator().get_language(SET_OF_TUPLES) == {('q', NLs('a', 'c', 'q', 'b'), 'x', 'y', 'z'), (NLs('a', 'c', 'q', 'b'), 'q', 'x', 'y', 'z'), ('q', 'x', 'y', 'z')}

        # >>> exp = (NLs('abc') + C('xyz')) @ C('axyz')
        # >>> assert exp.get_language(SET_OF_TUPLES) == exp.get_generator().get_language(SET_OF_TUPLES) == {(NLs('b', 'a', 'c'), 'a', 'x', 'y', 'z'), ('a', NLs('b', 'a', 'c'), 'x', 'y', 'z')}

        # >>> exp = C(Ls('xyz') , 'b', Ls('yz')) & C('v', 'b', 'v')['v':_]
        # >>> assert exp.get_language() == exp.get_generator().get_language() == {'yby', 'zbz'}
    """

    flattened = classmethod(flattened)
