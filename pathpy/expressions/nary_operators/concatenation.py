from .nary_operator import NAryOperator

__all__ = ['Concatenation']


class Concatenation(NAryOperator):
    """This class represents the concatenation of languages

    `Concatenation` is semantically equivalent to concatenation of
    languages. That is, `Concatenation(A, B)` is the set of the
    concatenation of each pair of strings `(a, b)` where `a` is
    generated by `A` and `b` is generated by `B`.

    `Concatenation` follows the following relations:
       A + E = A
       E + A = A
       E + E = E
       A + {} = {}
       {} + A = {}
    where `E` is the empty string and `A` is any expression.

    A concatenation may also be constructed by using + operator.

    Examples:
       >>> from pathpy import Union as U, Concatenation as C, Intersection as I, EMPTY_STRING

       >>> exp = U('ab') + C('xy')
       >>> assert exp.get_language() == exp.get_generator().get_language() == {'axy', 'bxy'}

       >>> exp = 'a' + I('xy')
       >>> assert exp.get_language() == exp.get_generator().get_language() == set()

       >>> exp = I('xy') + 'a'
       >>> assert exp.get_language() == exp.get_generator().get_language() == set()

       >>> assert EMPTY_STRING.get_language() == EMPTY_STRING.get_generator().get_language() == {''}
    """
