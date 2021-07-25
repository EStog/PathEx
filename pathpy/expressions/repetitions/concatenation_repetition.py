from .repetition import Repetition


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
        >>> from pathpy import Concatenation as C, LettersPossitiveUnion as L

        >>> assert ( (L('a')+2)*[1,2] ).as_(set) == {'aaaa', 'aa'}

        >>> assert ( C('ab')*... & C('ab')*2 ).as_(set) == {'', 'ab', 'abab'}

        >>> assert ( C('ab')*2 & C('ab')*... ).as_(set) == {'', 'ab', 'abab'}
    """


__all__ = ['ConcatenationRepetition']
