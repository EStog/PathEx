from pathex.expressions.nary_operators.difference import Difference
from pathex.expressions.nary_operators.intersection import Intersection
from pathex.expressions.nary_operators.shuffle import Shuffle
from pathex.expressions.nary_operators.synchronization import Synchronization
from pathex.expressions.repetitions.shuffle_repetition import ShuffleRepetition

from .machine import MachineMatchMismatch
from .match_functions import simple_match
from .mismatch_functions import simple_mismatch
from .simple_machine import SimpleMachine
from .visitors.difference_visitor import difference_visitor
from .visitors.intersection_visitor import intersection_visitor
from .visitors.shuffle_repetition_visitor import shuffle_repetition_visitor
from .visitors.shuffle_visitor import shuffle_visitor
from .visitors.synchronization_visitor import synchronization_visitor


class ExtendedMachine(SimpleMachine, MachineMatchMismatch):
    match = simple_match
    mismatch = simple_mismatch

    @classmethod
    def _populate_visitor(cls):
        super()._populate_visitor()
        cls.branches.register(Intersection, intersection_visitor)
        cls.branches.register(Synchronization, synchronization_visitor)
        cls.branches.register(Shuffle, shuffle_visitor)
        cls.branches.register(
            ShuffleRepetition, shuffle_repetition_visitor)
        cls.branches.register(Difference, difference_visitor)
