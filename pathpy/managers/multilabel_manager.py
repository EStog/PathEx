from __future__ import annotations

from abc import abstractmethod

from pathpy.expressions.expression import Expression

from .manager import Manager

__all__ = ['MultilabelManager']


class MultilabelManager(Manager):
    """This manager has the capability of register the checked labels in case they can not be generated in the moment. When the manager encounter a label that can be generated, it tries to update the information it has of the labels that were not able to generate previously.
    """

    def __init__(self, expression: Expression):
        self._labels: dict[object, object] = {}
        super().__init__(expression)

    @abstractmethod
    def _post_success(self, label: object) -> object: ...

    @abstractmethod
    def _post_failure(self, associate: object) -> object: ...

    @abstractmethod
    def _register_label_presence(self, label: object) -> object: ...

    @abstractmethod
    def _get_associate(self, label: object) -> object: ...

    @abstractmethod
    def _comply_condition_on_associate(self, associate: object) -> bool: ...

    @abstractmethod
    def _update_associate(self, associate: object) -> None: ...

    def _when_allowed(self, label: object) -> object:
        self._check_saved_labels()
        return self._post_success(label)

    def _when_not_allowed(self, label: object) -> object:
        associate = self._register_label_presence(label)
        return self._post_failure(associate)

    def _check_saved_labels(self):
        while True:
            for label in self._labels:
                associate = self._get_associate(label)
                if self._comply_condition_on_associate(associate):
                    if self._advance(label):
                        self._update_associate(associate)
                        break
            else:
                break
