from __future__ import annotations

from typing import Iterable


def simple_match(self, value1: object, value2: object) -> object:
    return value1 if value1 == value2 else None


def simple_unmatch(self, value1: object, value2: object) -> Iterable[object]:
    from pathpy.expressions.nary_operators.shuffle import Shuffle
    return [Shuffle(value1, value2)] if value1 != value2 else []
