from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from contextlib import contextmanager
from copy import copy
from functools import wraps

from pathex.adts.singleton import singleton
from pathex.expressions.expression import Expression
from pathex.expressions.nary_operators.concatenation import Concatenation
from pathex.expressions.nary_operators.intersection import Intersection
from pathex.expressions.nary_operators.union import Union
from pathex.generation.machines.machine import MachineMatch
from pathex.expressions.terms.empty_word import EMPTY_WORD

from .tag import Tag

__all__ = ['Manager']

# TODO: refactor by using Shuffle and Intersection


class Manager(ABC):
    """A generic abstract manager.
    """
    @singleton
    class _WaitingLabels:
        """The instance of this class is used to represent future labels to be matched with. The idea is to use an abstract replacement object that is to be concretized with the current waiting-labels expression.
        """
        pass

    @staticmethod
    def _waiting_labels_visitor(machine, exp):
        # return a visitor to the current waiting-labels expression
        return machine.branches(machine.waiting_labels_expression)

    def __init__(self, expression: Expression, machine: MachineMatch):
        self._waiting_labels = self._WaitingLabels()
        self._expression: object = Intersection.flattened(self._waiting_labels, expression)

        class CustomMachine(machine.__class__):
            waiting_labels_expression: object

            @classmethod
            def _populate_visitor(cls):
                super()._populate_visitor()
                cls.branches.register(self._WaitingLabels,
                                      self._waiting_labels_visitor)

        # Just in case ``machine`` has some attributes:
        machine = copy(machine)

        # Expand ``machine.branch`` with ``_waiting_labels_visitor``:
        machine.__class__ = CustomMachine

        self._machine: CustomMachine = machine

    @abstractmethod
    def _when_requested_match(self, label: object) -> object: ...

    @abstractmethod
    def _when_matched(self, label: object, label_info: object) -> object: ...

    @abstractmethod
    def _when_not_matched(self, label: object,
                          label_info: object) -> object: ...

    def match(self, label: object) -> object:
        """ This method is used to notify to the manager the presence of a given label.

        The manager then see if this label is allowed by checking if the internal expression can generate the given label.
        If the label is allowed or not, a respective action is taken.

        Args:
            label (object): The label to check for.
        """
        label_info = self._when_requested_match(label)
        if self._advance(label):
            return self._when_matched(label, label_info)
        else:
            return self._when_not_matched(label, label_info)

    def _advance(self, label: object) -> bool:
        new_alternatives = deque()
        # the waiting-labels expression is setted as a sequence consisting of the current label to be matched, followed by the rest of the labels that are to be matched
        self._machine.waiting_labels_expression = Concatenation(label, self._waiting_labels)
        alts = deque([self._expression])
        while alts:
            exp = alts.popleft()
            for head, tail in self._machine.branches(exp):
                if head == label:
                    new_alternatives.append(tail)
                elif head is EMPTY_WORD:
                    alts.append(tail)
        if new_alternatives:
            self._expression = Union.flattened(new_alternatives)
            return True
        else:
            return False

    def register(self, tag: Tag, func=None):
        """Decorator to mark a method as a region.

        Args:
            tag (Tag): A tag to mark the given funcion with.
        """
        def wrapper(wrapped):
            @wraps(wrapped)
            def f(*args, **kwargs):
                self.match(tag.enter)
                x = wrapped(*args, **kwargs)
                self.match(tag.exit)
                return x
            return f

        if func is None:
            return wrapper
        else:
            return wrapper(func)

    @contextmanager
    def region(self, tag: Tag):
        """Context manager to mark a piece of code as a region.

        Args:
            tag (Tag): A tag to mark the corresponding block with.
        """
        self.match(tag.enter)
        try:
            yield self
        finally:
            self.match(tag.exit)
