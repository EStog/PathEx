from __future__ import annotations

import multiprocessing as mp
import threading
from concurrent.futures import Future
from concurrent.futures import ProcessPoolExecutor as cfProcessPoolExecutor
from contextlib import contextmanager
from functools import wraps
from multiprocessing.managers import BaseManager, BaseProxy, SyncManager
from multiprocessing.pool import AsyncResult
from multiprocessing.pool import Pool as mpPool
from typing import Any, Callable, Iterable, TypeVar

from pathex.expressions.expression import Expression
from pathex.generation.machines.machine import MachineMatch

from .synchronizer import Synchronizer
from .tag import Tag

__all__ = ['process_synchronizer', 'get_synchronizer', 'process_register',
           'process_region', 'process', 'Pool', 'ProcessPoolExecutor']

Address = tuple[str, int]


class SynchronizerProxy(BaseProxy):
    """This class represents is a :class:`proxy <BaseProxy>` to a :class:`Synchronizer` object"""

    _exposed_ = ['match', 'requests', 'permits']

    def match(self, label: object) -> object:
        return self._callmethod('match', (label,))

    def requests(self, label: object) -> int:
        return self._callmethod('requests', (label,))

    def permits(self, label: object) -> int:
        return self._callmethod('permits', (label,))


def process_synchronizer(exp: Expression, machine: MachineMatch | None = None,
                         lock_class=threading.Lock, address=None, authkey=None, manager_class=BaseManager) -> SyncManager:

    synchronizer = Synchronizer(exp, machine, lock_class)

    class ProcessManager(manager_class):
        pass
    ProcessManager.register(typeid='get_synchronizer',
                            proxytype=SynchronizerProxy,
                            callable=lambda: synchronizer)
    manager = ProcessManager(address=address, authkey=authkey)
    manager.start()

    return manager


def get_synchronizer(address: Address, authkey: bytes = None) -> SynchronizerProxy:
    """Obtains a :ref:`proxy <multiprocessing-proxy-objects>` to a :class:`~.Synchronizer` retrieved from *address* and with the given *authkey*.
    """
    class ProcessManager(BaseManager):
        pass
    ProcessManager.register(typeid='get_synchronizer',
                            proxytype=SynchronizerProxy)
    manager = ProcessManager(address=address, authkey=authkey)
    manager.connect()
    return manager.get_synchronizer()


def process_register(tag: Tag, func=None, /, *, authkey=None):
    """Decorator to mark a method as a region (this version is for using with :mod:`multiprocessing`).

    .. warning::

       This version is meant to be used with :mod:`multiprocessing` only.

    Args:
        tag (Tag): A tag to mark the given funcion with.
    """
    def wrapper(wrapped):
        @wraps(wrapped)
        def f(address, *args, **kwargs):
            synchronizer = get_synchronizer(address, authkey)
            synchronizer.match(tag.enter)
            x = wrapped(*args, **kwargs)
            synchronizer.match(tag.exit)
            return x
        return f

    if func is None:
        return wrapper
    else:
        return wrapper(func)


@contextmanager
def process_region(tag: Tag, address, authkey=None):
    """Context manager to mark a piece of code as a region.

    .. warning::

       This version is meant to be used with :mod:`multiprocessing` only.

    Args:
        tag (Tag): A tag to mark the corresponding block with.
    """
    synchronizer = get_synchronizer(address, authkey)
    synchronizer.match(tag.enter)
    try:
        yield synchronizer
    finally:
        synchronizer.match(tag.exit)


def process(address, authkey=None, target=None, args=(), *p_args, **p_kwargs):
    """This is just a :class:`multiprocessing.Process` factory function that sets *address* and *authkey* as proper positional parameters to the given *target*"""
    return mp.Process(target=target, args=(address,)+tuple(args), *p_args, **p_kwargs)


_T = TypeVar('_T')


class Pool(mpPool):
    """This class is the analog to :class:`multiprocessing.Pool` but it provides :meth:`apply` and :meth:`apply_async` methods that automatically set *address* and *authkey* as proper positional arguments"""

    def __init__(self, address, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._address = address

    def apply(self, func: Callable[..., _T], args: Iterable[Any], *a_args, **a_kwargs) -> _T:
        return super().apply(func, args=(self._address,)+tuple(args),
                             *a_args, **a_kwargs)

    def apply_async(self, func: Callable[..., _T], args: Iterable[Any], *a_args, **a_kwargs) -> AsyncResult[_T]:
        return super().apply_async(func, args=(self._address,)+tuple(args),
                                   *a_args, **a_kwargs)


class ProcessPoolExecutor(cfProcessPoolExecutor):
    """This class is the analog to :class:`concurrent.futures.Pool` but it provides a :meth:`submit` method that automatically set *address* and *authkey* as proper positional arguments"""

    def __init__(self, address, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._address = address

    def submit(self, fn: Callable[..., _T], *args: Any, **kwargs: Any) -> Future[_T]:
        return super().submit(fn, *((self._address,)+args), **kwargs)
