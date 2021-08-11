from __future__ import annotations

from typing import Callable

from pathpy.expressions.expression import Expression

from .manager import Manager

__all__ = ['MultilabelManager']


class MultilabelManager(Manager):
    """This manager has the capability of register the checked labels in case they can not be generated in the moment. When the manager encounter a label that can be generated, it tries to update the information it has of the labels that were not able to generate previously.
    """

    def __init__(self, expression: Expression,
                 post_success: Callable[[MultilabelManager, object], None],
                 post_failure: Callable[[MultilabelManager, object], None],
                 register_label_presence: Callable[[MultilabelManager, object], object],
                 get_associate: Callable[[MultilabelManager, object], object],
                 comply_condition_on_associate: Callable[[MultilabelManager, object], bool],
                 update_associate: Callable[[MultilabelManager, object], None]):
        self._labels: dict[object, object] = {}
        self._post_success = post_success
        self._post_failure = post_failure
        self._register_label_presence = register_label_presence
        self._get_associate = get_associate
        self._comply_condition_on_associate = comply_condition_on_associate
        self._update_associate = update_associate

        def when_allowed(self, label):
            self._check_saved_labels()
            self._post_success(self, label)

        def when_not_allowed(self, label):
            obj = self._register_label_presence(self, label)
            self._post_failure(self, obj)

        super().__init__(expression, when_allowed, when_not_allowed)

    def _check_saved_labels(self):
        while True:
            for label in self._labels:
                obj = self._get_associate(self, label)
                if self._comply_condition_on_associate(self, obj):
                    if self._advance(label):
                        self._update_associate(self, obj)
                        break
            else:
                break
