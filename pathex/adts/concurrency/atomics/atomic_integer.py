import operator
import threading

from .atomic import Atomic

__all__ = ['AtomicInteger']


# TODO: Add other integer methods.

class AtomicInteger(Atomic):
    """An atomic integer. It has the same operation than Atomic, with comparison, sum and substraction.

    .. testsetup::

       from pathex.adts.concurrency.atomics.atomic_integer import AtomicInteger

    >>> a = AtomicInteger() # default to cero
    >>> a += 3
    >>> assert a == 3
    >>> assert a.value - 1 == 2
    >>> a -= 1
    >>> assert a < 3
    >>> assert a > 1
    """

    def __init__(self, value=0, lock_class=threading.Lock):
        super().__init__(value, lock_class=lock_class)

    @staticmethod
    def _check_value(value):
        if not isinstance(value, int):
            raise TypeError(f'value must be int, not {type(value)}')

    def _safe_modification_operation(self, op, value):
        self._check_value(value)
        with self._lock:
            self.__dict__['_value'] = op(self._value, value)

    def _unsafe_modification_operation(self, op, value):
        self._check_value(value)
        self.__dict__['_value'] = op(self._value, value)

    def _safe_set_value(self, value):
        self._check_value(value)
        return super()._safe_set_value(value)

    def _unsafe_set_value(self, value):
        self._check_value(value)
        return super()._unsafe_set_value(value)

    def _change_to_safe(self):
        self.__dict__[
            '_modification_operation'] = self._safe_modification_operation
        return super()._change_to_safe()

    def _change_to_unsafe(self):
        self.__dict__[
            '_modification_operation'] = self._unsafe_modification_operation
        return super()._change_to_unsafe()

    def __iadd__(self, value):
        self._modification_operation(operator.__iadd__, value)
        return self

    def __isub__(self, value):
        self._modification_operation(operator.__isub__, value)
        return self

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.value > other.value
        else:
            return self.value > other

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.value < other.value
        else:
            return self.value < other
