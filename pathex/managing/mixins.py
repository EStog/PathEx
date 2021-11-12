from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Hashable, Iterator

from pathex.managing.tag import Tag


class ManagerMixin(ABC):

    @abstractmethod
    def match(self, label: Hashable) -> object: ...

    @contextmanager
    def region(self, tag: Tag) -> Iterator[ManagerMixin]:
        """Context manager to mark a piece of code as a region.

        Args:
            tag (Tag): A tag to mark the corresponding block with.
        """
        self.match(tag.enter)
        try:
            yield self
        finally:
            self.match(tag.exit)


class LogbookMixin(ABC):

    @abstractmethod
    def requests(self, label: object) -> int:
        pass

    @abstractmethod
    def permits(self, label: object) -> int:
        pass
