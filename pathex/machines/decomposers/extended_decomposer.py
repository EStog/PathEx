from pathex.expressions.nary_operators.difference import Difference
from pathex.expressions.nary_operators.intersection import Intersection
from pathex.expressions.nary_operators.shuffle import Shuffle
from pathex.expressions.repetitions.shuffle_repetition import ShuffleRepetition
from pathex.machines.decomposers.decomposer import DecomposerMatchMismatch
from pathex.machines.decomposers.match_functions import simple_match
from pathex.machines.decomposers.mismatch_functions import simple_mismatch
from pathex.machines.decomposers.simple_decomposer import SimpleDecomposer
from pathex.machines.decomposers.visitors.difference_visitor import \
    difference_visitor
from pathex.machines.decomposers.visitors.intersection_visitor import \
    intersection_visitor
from pathex.machines.decomposers.visitors.shuffle_repetition_visitor import \
    shuffle_repetition_visitor
from pathex.machines.decomposers.visitors.shuffle_visitor import \
    shuffle_visitor


class ExtendedDecomposer(SimpleDecomposer, DecomposerMatchMismatch):
    match = simple_match
    mismatch = simple_mismatch

    @classmethod
    def _populate_transformer(cls):
        super()._populate_transformer()
        cls._transform.register(Intersection, intersection_visitor)
        cls._transform.register(Shuffle, shuffle_visitor)
        cls._transform.register(
            ShuffleRepetition, shuffle_repetition_visitor)
        cls._transform.register(Difference, difference_visitor)
