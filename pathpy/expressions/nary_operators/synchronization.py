from .nary_operator import NAryOperator


class Synchronization(NAryOperator):
    """
    `Synchronization` is semantically equivalent to a weak intersection of languages (sets of strings), that is, to see the "almost" common strings between the considered languages. The letters that are different are put as a shuffle in their corresponding places in the
    resulting strings.

    `Synchronization` (`@`) can be expressed recursively in the following manner.

    Let `a` and `b` be letters, `A` and `B` strings, and `E` the empty string.
        `a @ b = a`                     if `a == b`
        `a @ b = a // b`                if `a != b`
        `aA @ bB = (a @ b) + (A @ B)`

    Example:
        >>> from pathpy import Union as U, WILDCARD as _, Concatenation as C

        >>> exp = ( 'a' + U('xy') ) @ ( 'a' + U('yz') )
        >>> assert exp.as_(set) == {
        ...     'axy', 'ayx', 'axz', 'azx', 'ay', 'ayz', 'azy'}

        >>> exp = ( 'a' + U('xy') ) @ ( 'a' + U('yz') + 'w' )
        >>> assert exp.as_(set) == {
        ...     'axyw', 'ayxw', 'axzw', 'azxw', 'ayw', 'ayzw', 'azyw'}

        >>> exp = ( _ + U('xy') ) @ ( 'a' + U('yz') )
        >>> assert exp.as_(set, ignore_reification_errors=True) == {
        ...     'axy', 'ayx', 'axz', 'azx', 'ay', 'ayz', 'azy'}

        >>> exp = ( _ + U('xy') ) @ ( 'a' + (_|'z') )
        >>> assert exp.as_(set, ignore_reification_errors=True) == {'ax', 'ay', 'ayz', 'axz', 'azy', 'azx'}

        >>> exp = C('xabx')['x':_] @ ( C('a', _, _, 'a') | C(*'bab', _) )
        >>> assert exp.as_(set, ignore_reification_errors=True) == {'aaba', 'babb'}

        >>> exp = C('xab')['x':_] @ C('yby')['y':_]
        >>> assert exp.as_(set, ignore_reification_errors=True) == {'babb', 'bbab'}

        >>> from pathpy import LettersNegativeUnion as NL

        In the case of the presence of a negation there is an error in the case of a reification to a set of strings, because there are words that can not be determined.

        >>> exp = (NL('abc') + C('xyz')) @ C('qxyz')
        >>> assert exp.as_(set, ignore_reification_errors=True) == {'qxyz'}

        >>> exp = (NL('abc') + C('xyz')) @ C('axyz')
        >>> assert exp.as_(set, ignore_reification_errors=True) == set()

        >>> exp = (NL('abc') + C('xyz')) @ C('qxyz')
        >>> assert exp.as_(set, ignore_reification_errors=True) == {'qxyz'}
    """


__all__ = ['Synchronization']
