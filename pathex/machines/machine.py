from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

__all__ = ['Machine']


@dataclass(frozen=True)
class Machine(ABC):

    @abstractmethod
    def transform(self, exp: object) -> Any: ...
