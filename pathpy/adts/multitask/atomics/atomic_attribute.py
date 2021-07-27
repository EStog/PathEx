from .atomic import Atomic


class AtomicAttribute:
    """An attribute (a descriptor) that holds a variable whose value can be changed in concurrent-safe manner.

    >>> from threading import Lock, Thread
    >>> class A:
    ...     atomic_attr = AtomicAttribute(Lock, 5)
    ...
    ...     def __init__(self):
    ...         assert self.atomic_attr == 5
    ...         self.atomic_attr = 10
    ...         assert self.atomic_attr == 10

    >>> a = A()
    >>> assert a.atomic_attr == 10

    >>> def f():
    ...     a.atomic_attr = [3, 4, 5]

    >>> def g():
    ...     return a.atomic_attr

    >>> t, t1 = Thread(target=f), Thread(target=g)
    >>> t.start(); t1.start()
    >>> t.join(); t1.join()
    >>> assert a.atomic_attr == [3, 4, 5]

    If the attribute is deleted, it will be re-created with a default value if consulted. So it is better to check __dict__ in order to see if the attribute exists. Deleting an already deleted attribute has no effect

    >>> del a.atomic_attr
    >>> assert not 'atomic_attr' in vars(a)
    >>> del a.atomic_attr
    >>> assert not 'atomic_attr' in vars(a)
    >>> assert a.atomic_attr == 5
    """

    def __init__(self, lock_class, default=None):
        self._lock_class = lock_class
        self._default = default

    def _get_default_object(self):
        if callable(self._default):
            default = self._default()
        else:
            default = self._default
        return Atomic(self._lock_class, default)

    def _get_object(self, instance):
        return instance.__dict__.setdefault(
            self._attribute_name, self._get_default_object())

    def __set_name__(self, owner, name):
        self._attribute_name = name

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError(
                f"type object '{owner.__name__}' has no attribute '{self._attribute_name}'")
        else:
            return self._get_object(instance).get_value()

    def __set__(self, instance, value):
        self._get_object(instance).set_value(value)

    def __delete__(self, instance):
        try:
            del instance.__dict__[self._attribute_name]
        except KeyError:
            pass
