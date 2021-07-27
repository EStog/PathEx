class Atomic:
    """This is an object that holds a variable whose value can be changed in concurrent-safe manner.

    >>> from threading import Lock, Thread
    >>> a = Atomic(Lock, 1)
    >>> assert a.value == 1
    >>> a.value = 5
    >>> assert a.value == 5

    >>> def f():
    ...     a.value = [3, 4, 5]

    >>> def g():
    ...     return a.value

    >>> t = Thread(target=f)
    >>> t1 = Thread(target=g)
    >>> t.start()
    >>> t1.start()
    >>> t.join()
    >>> t1.join()
    >>> assert a.value == [3, 4, 5]
    """

    def __init__(self, lock_class, value=None):
        self._value = value
        self._lock = lock_class()

    def get_value(self):
        with self._lock:
            return self._value

    def set_value(self, value):
        with self._lock:
            self._value = value

    def del_value(self):
        raise AttributeError('Value can not be deleted')

    value = property(get_value, set_value, del_value,
                     'The value of the atomic object')
