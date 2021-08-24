from __future__ import annotations

from pathpy.expressions.expression import Expression
from pathpy.generation.machines.extended_simple_machine import \
    ExtendedSimpleMachine
from pathpy.generation.machines.machine import Machine, MachineWithMatch
from pathpy.managing.label import Label

from .manager import Manager

__all__ = ['TraceChecker']


class TraceChecker(Manager):
    """This class is just to demonstrate the use of manager for other tasks different than task synchronization.

    >>> from pathpy import Tag
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
    AssertionError: Enter(func_c) is not allowed after Exit(func_a)
    """

    def __init__(self, expression: Expression, machine: MachineWithMatch | None = None):
        if machine is None:
            machine = ExtendedSimpleMachine()
        super().__init__(expression, machine)
        self._last_seen_label = None

    def _when_requested_match(self, label: Label) -> object:
        pass

    def _when_matched(self, label: Label, label_info: object) -> bool:
        self._last_seen_label = label
        return False

    def _when_not_matched(self, label: Label, label_info: object) -> object:
        if self._last_seen_label is None:
            return f'{label} is not allowed as first label'
        else:
            return f'{label} is not allowed after {self._last_seen_label}'

    def match(self, label: Label) -> object:
        assert not (x := super().match(label)), x
