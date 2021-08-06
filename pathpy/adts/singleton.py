from typing import TypeVar

_T = TypeVar('_T')

import threading
import re

def singleton(wrapped_class: type[_T]) -> type[_T]:
    """Makes a class singleton

    Use it as a decorator:

    >>> from dataclasses import dataclass

    >>> @singleton
    ... @dataclass(init=False)
    ... class A:
    ...     attribute: int
    ...
    ...     def __init__(self, attribute: int):
    ...         self.attribute = attribute + 1

    Any call to the class will return the same object.
    The first call will make proper initialization, but
    subsequent calls will ignore the arguments. It is
    allowed to call the class without arguments after
    the first call.
    Also, this class does not provides an instance attribute.
    Use the class call instead or a previously assigned variable.

    >>> try:
    ...     A()
    ... except TypeError:
    ...     pass # Right!
    ... else:
    ...     print('Wrong')
    >>> instance = A(23)
    >>> assert instance is A(44) is A() is A(11)
    >>> assert A().attribute == instance.attribute == 24
    >>> assert not hasattr(A(), 'instance')

    Singleton classes can not be subclassed:

    >>> try:
    ...     class B(A):
    ...         pass
    ... except TypeError:
    ...     pass # Right!
    ... else:
    ...     print('Wrong!')
    """
    instance = None
    instance_hash = None
    lock = threading.Lock()

    def firstnew(cls, *init_args, **init_kwargs):
        nonlocal instance, instance_hash
        with lock:  # just in case the very remote possibility of a race condition
            if instance is None:
                if '__old_new__' in cls.__dict__:
                    instance = cls.__old_new__(cls, *init_args, **init_kwargs)
                else:
                    instance = object.__new__(cls)
                try:
                    cls.__init__(instance, *init_args, **init_kwargs)
                except:
                    instance = None # rollback changes
                    raise

                try:
                    instance_hash = hash(instance)
                except TypeError:
                    pass
                else:
                    cls.__hash__ = lambda self: instance_hash

                # All destructions must be done after initializations finished properly,
                # that is, without unexpected exceptions.
                cls.__new__ = secondnew
                cls.__init__ = lambda x, *args, **kwargs: None
                if '__old_new__' in cls.__dict__:
                    delattr(cls, '__old_new__')

        return instance

    def secondnew(cls, *init_args, **init_kwargs):
        return instance

    @classmethod
    def __init_subclass__(cls, /, *args, **kwargs):
        raise TypeError('Singleton class can not be subclassed')

    def __repr__(self):
        name = self.__class__.__name__
        s = re.sub(r'[A-Z]', r'_\g<0>', name[1:])
        return f"<{name[0]}{s}>".upper()

    if '__new__' in wrapped_class.__dict__:
        wrapped_class.__old_new__ = wrapped_class.__new__
    wrapped_class.__new__ = firstnew
    wrapped_class.__init_subclass__ = __init_subclass__
    wrapped_class.__repr__ = __repr__

    return wrapped_class


__all__ = ['singleton']
