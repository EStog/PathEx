from __future__ import annotations

from functools import singledispatchmethod

from pathex.expressions.nary_operators.concatenation import Concatenation
from pathex.expressions.nary_operators.union import Union
from pathex.expressions.repetitions.concatenation_repetition import \
    ConcatenationRepetition
from pathex.expressions.terms.letter import Letter

from .machine import Machine
from .visitors.concatenation_repetition_visitor import \
    concatenation_repetition_visitor
from .visitors.concatenation_visitor import concatenation_visitor
from .visitors.letter_visitor import letter_visitor
from .visitors.object_visitor import object_visitor
from .visitors.union_visitor import union_visitor


class SimpleMachine(Machine):
    @classmethod
    def _populate_visitor(cls):
        cls.branches = singledispatchmethod(object_visitor)
        cls.branches.register(Letter, letter_visitor)
        cls.branches.register(Concatenation, concatenation_visitor)
        cls.branches.register(Union, union_visitor)
        cls.branches.register(ConcatenationRepetition,
                              concatenation_repetition_visitor)
