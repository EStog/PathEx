from pathex.expressions.nary_operators.nary_operator import NAryOperator

__all__ = ['Union']


class Union(NAryOperator):
    """This class represents a union of languages.

    A union of languages is equivalent to the union of the sets.

    >>> from pathex.expressions.aliases import *
    >>> exp = U('abcd')
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'a', 'b', 'c', 'd'}

    A union may also be constructed by using the | operator.

    >>> exp = U('ab') | U('cd')
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'a', 'b', 'c', 'd'}

    >>> exp = C('ab') | C('cd')
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'ab', 'cd'}

    >>> exp = 'a' | ( 'b' + U('cd') )
    >>> assert exp.get_language() == exp.get_generator().get_language() == {'a', 'bc', 'bd'}
    """
