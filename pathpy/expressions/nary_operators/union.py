from .nary_operator import NAryOperator


class Union(NAryOperator):
    """This class represents a union of languages.

    A union of languages is equivalent to the union of the sets.

    >>> from pathpy import Union as U
    >>> assert U('abcd').language() == {'a', 'b', 'c', 'd'}

    A union may also be constructed by using the | operator.

    >>> assert (U('ab') | U('cd')).language() == {'a', 'b', 'c', 'd'}
    """
    pass


__all__ = ['Union']
