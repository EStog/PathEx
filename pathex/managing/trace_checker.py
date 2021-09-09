from __future__ import annotations

from pathex.expressions.expression import Expression
from pathex.machines.decomposers.extended_decomposer_compalphabet import \
    ExtendedDecomposerCompalphabet
from pathex.machines.decomposers.decomposer import DecomposerMatch
from .manager import Manager

__all__ = ['TraceChecker']


class TraceChecker(Manager):
    """This class is just to demonstrate the use of manager for other tasks different than task synchronization.

    >>> from pathex import Tag
    >>> a, b, c = Tag.named('func_a', 'func_b', 'func_c')
    >>> trace_checker = TraceChecker((a+b+c)*...)

    >>> @trace_checker.register(a)
    ... def func_a():
    ...     return 'func_a'

    >>> @trace_checker.register(b)
    ... def func_b():
    ...     return 'func_b'

    >>> @trace_checker.register(c)
    ... def func_c():
    ...     return 'func_c'

    >>> func_a(), func_b(), func_c()
    ('func_a', 'func_b', 'func_c')

    >>> func_a(), func_c(), func_b()
    Traceback (most recent call last):
        ...
    AssertionError: func_c.enter is not allowed after func_a.exit
    """

    def __init__(self, expression: Expression, machine: DecomposerMatch | None = None):
        if machine is None:
            machine = ExtendedDecomposerCompalphabet()
        super().__init__(expression, machine)
        self._last_seen_label = None

    def _when_requested_match(self, label: object) -> object:
        pass

    def _when_matched(self, label: object, label_info: object) -> bool:
        self._last_seen_label = label
        return False

    def _when_not_matched(self, label: object, label_info: object) -> object:
        if self._last_seen_label is None:
            return f'{label} is not allowed as first label'
        else:
            return f'{label} is not allowed after {self._last_seen_label}'

    def match(self, label: object) -> object:
        assert not (x := super().match(label)), x
