from .nary_operator import NAryOperator


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

       >>> assert ( U('ab') + C('xy') ).as_set_of_str() == {'axy', 'bxy'}

       >>> assert ( 'a' + I('xy') ).as_set_of_str() == set()

       >>> assert ( I('xy') + 'a' ).as_set_of_str() == set()

       >>> assert EMPTY_STRING.as_set_of_str() == {''}
    """


__all__ = ['Concatenation']
