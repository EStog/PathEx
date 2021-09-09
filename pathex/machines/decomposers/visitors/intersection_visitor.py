from __future__ import annotations

from ..decomposer import Branches, DecomposerMatch
from .decorators import matching_operator_visitor, nary_operator_visitor

__all__ = ['intersection_visitor']

@nary_operator_visitor
@matching_operator_visitor
def intersection_visitor(decomposer: DecomposerMatch, head1, head2, tail) -> Branches:
    # `a & b = a`                 if `a == b`
    for match in decomposer.match(head1, head2):
        yield match, tail
    # `a & b = {}`                if `a != b`
