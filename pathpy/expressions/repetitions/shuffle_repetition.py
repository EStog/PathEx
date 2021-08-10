from .repetition import Repetition


class ShuffleRepetition(Repetition):
    """
    `ShuffleRepetition` is semantically equivalent to range-bounded shuffle repetition of its argument. That is, `ShuffleRepetition(A, n, m)` means that expression `A` must be repeated using `Shuffle` from `n` to `m` times`.
    For example:
        `ShuffleRepetition(ab, 1, 3) = ab | (ab // ab) | (ab // ab // ab)`
    where `+` is `Concatenation` and `|` is `Union`.

    If the upper bound is `inf`, the repetition is boundedless in termination, whilst if the lower bound is `0`, the entire repetition is optional.
    For example:
        `ShuffleRepetition(ab, 1, inf) = ab | (ab // ab) | (ab // ab // ab) | ......`
        `ShuffleRepetition(ab, 0, 3) = E | ab | (ab // ab) | (ab // ab // ab) | ......`
        `ShuffleRepetition(ab, 0, inf) = E | ab | (ab // ab) | (ab // ab // ab) | ......`
    where `E` is the empty string.

    To specify a valid repetition `ShuffleRepetition(A, n, m)` the following conditions must hold:
    - n is possitive integer or cero.
    - m is possitive integer (not cero) or `inf`.
    - n <= m.
    - A is not the empty string.

    `ShuffleRepetition` can be expressed recursively in the following manner:
        `ShuffleRepetition(A, 1, 1) =  A`
        `ShuffleRepetition(A, 0, m) = E | ShuffleRepetition(A, 1, m))`
            if `m > 1`
        `ShuffleRepetition(a+B, n, m) = ConcatenationRepetition(a, n, m)`
            if `a` is a letter and `B` is the empty string
        `ShuffleRepetition(a+B, n, m) = a + (B // ShuffleRepetition(aB, n-1, m-1))`
            if `n > 0` and `a` is letter and `B` is not the empty string

    Examples:
        >>> from pathpy import Shuffle as S, Concatenation as C

        >>> exp = S('ab')%[1,2]
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'ab', 'ba', 'abab', 'abba', 'baba', 'aabb', 'baab', 'bbaa'}

        >>> exp &= C('ab')%...
        >>> assert exp.get_language() == exp.get_generator().get_language() == {'ab', 'abab', 'aabb'}
    """


__all__ = ['ShuffleRepetition']
