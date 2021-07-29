import threading
from typing import Any


class Atomic:
    """An object that holds a variable whose value can be changed in concurrent-safe manner.

    The value may be consulted and assigned using `obj.value`. Also `obj.get_value` and `obj.set_value` may be used to consult and assign the value.

    >>> from threading import Thread
    >>> a = Atomic(1)
    >>> assert a == 1 # using __eq__
    >>> a.value = 5
    >>> assert a.value == 5

    >>> def f():
    ...     a.set_value([3, 4, 5]) # same as a.value = [3, 4, 5]

    >>> def g():
    ...     return a.get_value() # same as return a.value

    >>> t, t1 = Thread(target=f), Thread(target=g)
    >>> t.start(); t1.start()
    >>> t.join(); t1.join()
    >>> assert a.value == [3, 4, 5]

    >>> try:
    ...     del a.value
    ... except AttributeError:
    ...     pass # Right!
    ... else:
    ...     print('Wrong!')

    Atomic values may be used as context managers. This is helpful if some related actions must be done while holding the lock of the atomic. `__enter__` will return the object itself. Any operation of the atomic object called inside the managed block will be effected without acquiring the underlier lock.

    >>> with a:
    ...     # adicional actions here
    ...     a.value = 4
    ...     # adicional actions here
    ...     assert a == 4
    ...     a.value += 1
    >>> assert a == 5
    """

    def __init__(self, value: Any = None, lock_class=threading.Lock):
        self.__dict__.update(_value=value, _lock=lock_class())
        self._change_to_safe()

    def __getattr__(self, name: str) -> Any:
        if name == 'value':
            return self.get_value()
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == 'value':
            self.set_value(value)
        else:
            object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        if name == 'value':
            raise AttributeError('Value can not be deleted')
        else:
            object.__delattr__(self, name)

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return self.value == other

    def __enter__(self):
        self._lock.acquire()
        self._change_to_unsafe()
        return self

    def __exit__(self, *args, **kwargs):
        self._change_to_safe()
        self._lock.release()

    def _safe_get_value(self):
        with self._lock:
            return self._value

    def _safe_set_value(self, value):
        with self._lock:
            self.__dict__['_value'] = value

    def _unsafe_get_value(self):
        return self._value

    def _unsafe_set_value(self, value):
        self.__dict__['_value'] = value

    def _change_to_safe(self):
        self.__dict__['get_value'] = self._safe_get_value
        self.__dict__['set_value'] = self._safe_set_value

    def _change_to_unsafe(self):
        self.__dict__['get_value'] = self._unsafe_get_value
        self.__dict__['set_value'] = self._unsafe_set_value
