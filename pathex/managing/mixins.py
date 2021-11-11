from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Hashable

from pathex.managing.tag import Tag


class ManagerMixin(ABC):

    @abstractmethod
    def match(self, label: Hashable) -> object: ...

    def region(self, tag: Tag):
        """Context manager and decorator to mark a piece of code as a region.

        Args:
            tag (Tag): A tag to mark the corresponding block with.
        """
        from pathex.managing.region import Region
        return Region(self, tag)


class LogbookMixin(ABC):

    @abstractmethod
    def requests(self, label: object) -> int:
        pass

    @abstractmethod
    def permits(self, label: object) -> int:
        pass
