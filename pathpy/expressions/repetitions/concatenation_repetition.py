from .repetition import Repetition

__all__ = ['ConcatenationRepetition']

class ConcatenationRepetition(Repetition):
    """
    `ConcatenationRepetition` is semantically equivalent to range-bounded
    concatenation repetition of its argument. That is, `ConcatenationRepetition(A, n, m)` means that expression `A` must be repeated using `Concatenation` from `n` to `m` times`.
    For example:
        `ConcatenationRepetition(ab, 1, 3) = ab | abab | ababab`
    where `|` is `Union`.
    If the upper bound is `inf`, the repetition is boundedless in termination, whilst if the lower bound is `0`, the entire repetition is optional.
    For example:
        `ConcatenationRepetition(ab, 1, inf) = ab | abab | ababab | ......`
        `ConcatenationRepetition(ab, 0, 3) = E | ab | abab | ababab | ......`
        `ConcatenationRepetition(ab, 0, inf) = E | ab | abab | ababab | ......`
    where `E` is the empty string.
    To specify a valid repetition `ConcatenationRepetition(A, n, m)` the following conditions must hold:
    - n is possitive integer or cero.
    - m is possitive integer (not cero) or `inf`.
    - n <= m.
    - A is not the empty string.

    `ConcatenationRepetition` can be expressed recursively in the following manner:
        `ConcatenationRepetition(A, 1, 1) =  A`
        `ConcatenationRepetition(A, 0, m) = E | ConcatenationRepetition(A, 1, m))`
            if `m > 1`
        `ConcatenationRepetition(A, n, m) = A + ConcatenationRepetition(A, n-1, m-1)`
            if `n > 0`

    Examples:
        >>> from pathpy.expressions.aliases import *
        >>> from pathpy import EMPTY_WORD

        >>> exp = (L('a')+2)*[1,2]
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'aaaa', 'aa'}

        >>> exp = C('ab')*... & C('ab')*2
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'', 'ab', 'abab'}

        >>> exp = C('ab')*2 & C('ab')*...
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'', 'ab', 'abab'}

        >>> exp1 = (C('ab') | EMPTY_WORD) + 'x'
        >>> exp2 = C('ab') * 'x'
        >>> assert exp1.get_language() == exp2.get_language() == exp1.get_generator().get_language()  == exp2.get_generator().get_language() == {'x', 'abx'}
    """
