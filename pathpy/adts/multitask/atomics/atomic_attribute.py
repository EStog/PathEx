import threading

from .atomic import Atomic


class AtomicAttribute:
    """An attribute (a descriptor) that holds a variable whose value can be changed in concurrent-safe manner.
    In order to avoid race conditions, the first use of the attribute must be done in a concurrent-safe moment, for example, in object creation (__new__) or customization (__init__).

    >>> from threading import Lock, Thread
    >>> class A:
    ...     atomic_attr = AtomicAttribute(5)
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

    In order to avoid race conditions, the atomic attribute can not be deleted.

    >>> try:
    ...     del a.atomic_attr
    ... except AttributeError:
    ...     pass # Right!
    ... else:
    ...     print('Wrong!')

    If lock_class is a string X, then the attribute of the instance of the owner class with name X will be used as lock_class

    >>> class A:
    ...     atomic_attr = AtomicAttribute(default=7, lock_class='instance_lock_class')
    ...
    ...     def __init__(self, instance_lock_class):
    ...         self.instance_lock_class = instance_lock_class

    >>> a = A(Lock)
    >>> assert a.atomic_attr == 7
    >>> assert type(a.__dict__['atomic_attr']._lock) == type(Lock())
    """

    def __init__(self, default=None, lock_class=threading.Lock,
                 atomic_class: type[Atomic] = Atomic):
        self._default = default
        self._lock_class = lock_class
        self._atomic_class = atomic_class
        self._get_object = self._create_get_object

    def _get_default_object(self, instance):
        default = self._default() if callable(self._default) else self._default
        lock_class = getattr(instance, self._lock_class) \
            if isinstance(self._lock_class, str) else self._lock_class
        return self._atomic_class(value=default, lock_class=lock_class)

    def _create_get_object(self, instance):
        obj = self._get_default_object(instance)
        instance.__dict__[self._attribute_name] = obj
        self._get_object = self._direct_get_object
        return obj

    def _direct_get_object(self, instance):
        return instance.__dict__[self._attribute_name]

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
        raise AttributeError('AtomicAttribute can not be deleted')
