from __future__ import annotations

from functools import singledispatchmethod
from pathex.adts.containers.ordered_set import OrderedSet
from typing import Collection

from pathex.adts.collection_wrapper import (CollectionWrapper,
                                            get_collection_wrapper)
from pathex.expressions.nary_operators.concatenation import Concatenation
from pathex.expressions.nary_operators.intersection import Intersection
from pathex.expressions.nary_operators.nary_operator import NAryOperator
from pathex.expressions.nary_operators.union import Union
from pathex.expressions.repetitions.repetition import Repetition
from pathex.expressions.repetitions.concatenation_repetition import ConcatenationRepetition
from pathex.expressions.repetitions.shuffle_repetition import ShuffleRepetition

from .machine import Machine


class Simplifier(Machine):

    def _flattened(self, cls: type[NAryOperator],
                   collection: CollectionWrapper[object],
                   args: Collection[object]):
        new_args = collection()
        for exp in args:
            if isinstance(exp, cls):
                new_args.extend(exp.arguments)
            else:
                new_args.put(exp)
        return new_args

    def _flattened_without_repetition(self, cls: type[NAryOperator], args: Collection[object]):
        return self._flattened(cls, get_collection_wrapper(OrderedSet, OrderedSet.append, OrderedSet.extend), args)

    def _flattened_with_repetition(self, cls: type[NAryOperator], args: Collection[object]):
        return self._flattened(cls, get_collection_wrapper(list, list.append, list.extend), args)

    def _give_nary(self, op_class: type[NAryOperator], args: Collection):
        length = len(args)
        assert length > 0, 'arguments length should never be cero'
        if length == 1:
            return next(iter(args))
        else:
            return op_class(args)

    def _args_transformer(self, args: Collection):
        new_args = []
        for a in args:
            new_args.append(self.transform(a))
        return new_args

    @singledispatchmethod  # type: ignore
    def transform(self, exp: object) -> object:
        return exp

    @transform.register(NAryOperator)
    def _transform_nary(self, exp: NAryOperator):
        return self._give_nary(exp.__class__, self._args_transformer(exp.arguments))

    @transform.register(Concatenation)
    def _transform_concatenation(self, exp: Concatenation):
        return self._give_nary(
            Concatenation,
            # tuple( Not necessary if NAryOperator does this in its constructor
                self._flattened_with_repetition(
                    Concatenation,
                    self._args_transformer(exp.arguments))
                    # )
            )

    def _transform_aci(self, exp: Union | Intersection):
        """Makes transformations considering the expression as an associative, conmutative and idempotent nary operator.
        """
        cls = exp.__class__
        return self._give_nary(
            cls,
            # tuple( Not necessary if NAryOperator does this in its constructor
                self._flattened_without_repetition(
                    cls,
                    self._args_transformer(exp.arguments))
                    # )
            )

    transform.register(Union, _transform_aci)
    transform.register(Intersection, _transform_aci)

    def _transform_repetition(self, exp: Repetition):
        arg = self.transform(exp.argument)
        # a+1 = a
        if exp.lower_bound == exp.upper_bound == 1:
            return arg
        else:
            return exp.__class__(self.transform(arg), exp.lower_bound, exp.upper_bound)

    transform.register(ConcatenationRepetition, _transform_repetition)
    transform.register(ShuffleRepetition, _transform_repetition)
