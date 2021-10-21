from __future__ import annotations

from functools import singledispatchmethod

from pathex.expressions.nary_operators.concatenation import Concatenation
from pathex.expressions.nary_operators.union import Union
from pathex.expressions.repetitions.concatenation_repetition import \
    ConcatenationRepetition
from pathex.expressions.terms.letter import Letter
from pathex.machines.decomposers.decomposer import Decomposer
from pathex.machines.decomposers.visitors.concatenation_repetition_visitor import \
    concatenation_repetition_visitor
from pathex.machines.decomposers.visitors.concatenation_visitor import \
    concatenation_visitor
from pathex.machines.decomposers.visitors.letter_visitor import letter_visitor
from pathex.machines.decomposers.visitors.object_visitor import object_visitor
from pathex.machines.decomposers.visitors.union_visitor import union_visitor


class SimpleDecomposer(Decomposer):
    @classmethod
    def _populate_transformer(cls):
        cls._transform = singledispatchmethod(object_visitor)
        cls._transform.register(Letter, letter_visitor)
        cls._transform.register(Concatenation, concatenation_visitor)
        cls._transform.register(Union, union_visitor)
        cls._transform.register(ConcatenationRepetition,
                                concatenation_repetition_visitor)
