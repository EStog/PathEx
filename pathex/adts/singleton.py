import re
import threading
from typing import TypeVar

__doc__ = f"""

Singleton decorator
===================

:Module: ``{__name__}``

.. sectionauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>
.. codeauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>

---------------------------------------------------------------

This module provides a :func:`~.singleton` decorator. Although it may seem that this has little usefulness in Python (because its inherent dynamic nature), the idea is to diminsh the possibilities in that an error may be committed, and to enforce some memory optimization by using only one instance of the decorated class.

.. include:: ../non_essential_disclamer.txt

.. todo:: development

   .. todo:: Review and finish
"""

__all__ = ['singleton']


T = TypeVar('T')


def singleton(wrapped_class: type[T]) -> type[T]:
    """Makes a class singleton

    Use it as a decorator:

    .. testsetup::

       from pathex.adts.singleton import singleton

    >>> from dataclasses import dataclass

    >>> @singleton
    ... @dataclass(init=False)
    ... class SingletonClass:
    ...     attribute: int
    ...
    ...     def __init__(self, attribute: int):
    ...         self.attribute = attribute + 1

    Any call to the class will return the same object. The first call will make proper initialization, but subsequent calls will ignore the arguments. It is allowed to call the class without arguments after the first call. Use the class call instead or a previously assigned variable.

    >>> try:
    ...     SingletonClass()
    ... except TypeError:
    ...     pass # Right!
    ... else:
    ...     print('Wrong')
    >>> instance = SingletonClass(23)
    >>> assert instance is SingletonClass(44) is SingletonClass() is SingletonClass(11)
    >>> assert SingletonClass().attribute == instance.attribute == 24
    >>> assert not hasattr(SingletonClass(), 'instance')

    Singleton classes can not be subclassed:

    >>> try:
    ...     class B(SingletonClass):
    ...         pass
    ... except TypeError:
    ...     pass # Right!
    ... else:
    ...     print('Wrong!')

    The representation of the singleton instance is constructed from the name of the class:

    >>> assert repr(SingletonClass()) == '<SINGLETON_CLASS>'
    >>> @singleton
    ... class _A_Class:
    ...     pass
    >>> assert repr(_A_Class()) == '<_A_CLASS>'
    """
    instance = None
    lock = threading.Lock()

    def firstnew(cls, *init_args, **init_kwargs):
        nonlocal instance
        with lock:  # just in case the very remote possibility of a race condition
            if instance is None:
                if '__old_new__' in cls.__dict__:
                    instance = cls.__old_new__(cls, *init_args, **init_kwargs)
                else:
                    instance = object.__new__(cls)
                try:
                    cls.__init__(instance, *init_args, **init_kwargs)
                except:
                    instance = None  # rollback changes
                    raise


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

    def __hash__(self):
        return hash(id(self))

    def __repr__(self):
        name = self.__class__.__name__
        s = re.sub(r'(?<!^)(?<!_)[A-Z]', r'_\g<0>', name)
        return f"<{s}>".upper()

    if '__new__' in wrapped_class.__dict__:
        wrapped_class.__old_new__ = wrapped_class.__new__
    wrapped_class.__new__ = firstnew
    wrapped_class.__init_subclass__ = __init_subclass__
    wrapped_class.__repr__ = __repr__
    wrapped_class.__hash__ = __hash__

    return wrapped_class
