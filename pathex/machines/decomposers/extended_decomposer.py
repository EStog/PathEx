from pathex.expressions.nary_operators.difference import Difference
from pathex.expressions.nary_operators.intersection import Intersection
from pathex.expressions.nary_operators.shuffle import Shuffle
from pathex.expressions.nary_operators.synchronization import Synchronization
from pathex.expressions.repetitions.shuffle_repetition import ShuffleRepetition

from .decomposer import DecomposerMatchMismatch
from .match_functions import simple_match
from .mismatch_functions import simple_mismatch
from .simple_decomposer import SimpleDecomposer
from .visitors.difference_visitor import difference_visitor
from .visitors.intersection_visitor import intersection_visitor
from .visitors.shuffle_repetition_visitor import shuffle_repetition_visitor
from .visitors.shuffle_visitor import shuffle_visitor
from .visitors.synchronization_visitor import synchronization_visitor


class ExtendedDecomposer(SimpleDecomposer, DecomposerMatchMismatch):
    match = simple_match
    mismatch = simple_mismatch

    @classmethod
    def _populate_transformer(cls):
        super()._populate_transformer()
        cls._transform.register(Intersection, intersection_visitor)
        cls._transform.register(Synchronization, synchronization_visitor)
        cls._transform.register(Shuffle, shuffle_visitor)
        cls._transform.register(
            ShuffleRepetition, shuffle_repetition_visitor)
        cls._transform.register(Difference, difference_visitor)
