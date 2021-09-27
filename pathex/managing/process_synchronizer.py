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
from pathex.machines.decomposers.decomposer import DecomposerMatch

from .synchronizer import Synchronizer
from .tag import Tag

__all__ = ['process_manager', 'get_synchronizer', 'process_register',
           'process_region', 'process', 'Pool', 'ProcessPoolExecutor']

Address = tuple[str, int]


class SynchronizerProxy(BaseProxy):
    """This class represents is a :class:`proxy <multiprocessing.managers.BaseProxy>` to a :class:`~.Synchronizer` object."""

    _exposed_ = ['match', 'requests', 'permits']

    def match(self, label: object) -> object:
        return self._callmethod('match', (label,))

    def requests(self, label: object) -> int:
        return self._callmethod('requests', (label,))

    def permits(self, label: object) -> int:
        return self._callmethod('permits', (label,))


def process_manager(exp: Expression, decomposer: DecomposerMatch | None = None,
                    lock_class=threading.Lock, address=None, authkey=None, manager_class=BaseManager) -> SyncManager:
    """Returns a new :class:`multiprocessing.managers.BaseManager` to be used to store shared data. This function should be called in the main process after initializing other processes. The address of the returned object should be passed to the mechanisms that PathEx provides to initialize subprocesses, aka, :class:`~pathex.managing.process_synchronizer.ProcessPoolExecutor`, :class:`~pathex.managing.process_synchronizer.Pool` and :class:`~pathex.managing.process_synchronizer.process`."""

    synchronizer = Synchronizer(exp, decomposer, lock_class)

    class ProcessManager(manager_class):
        get_synchronizer: Callable[[], SynchronizerProxy]

    ProcessManager.register(typeid='get_synchronizer',
                            proxytype=SynchronizerProxy,
                            callable=lambda: synchronizer)
    manager = ProcessManager(address=address, authkey=authkey)
    manager.start()

    return manager


def get_synchronizer(address: Address, authkey: bytes | None = None) -> SynchronizerProxy:
    """Obtains a :ref:`proxy <multiprocessing-proxy_objects>` to a :class:`~.Synchronizer` retrieved from ``address`` and with the given ``authkey``.
    """
    class ProcessManager(BaseManager):
        pass
    ProcessManager.register(typeid='get_synchronizer',
                            proxytype=SynchronizerProxy)
    manager = ProcessManager(address=address, authkey=authkey)
    manager.connect()
    return manager.get_synchronizer()


def process_register(tag: Tag, func=None, /, *, authkey=None):
    """Decorator to mark a method as a region. The ``tag`` is the name of the region.

    .. warning::

       This version is meant to be used with :mod:`multiprocessing` only.
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
    """Context manager to mark a piece of code named by ``tag`` as a region.

    .. warning::

       This version is meant to be used with :mod:`multiprocessing` only.
    """
    synchronizer = get_synchronizer(address, authkey)
    synchronizer.match(tag.enter)
    try:
        yield synchronizer
    finally:
        synchronizer.match(tag.exit)


def process(address, authkey: bytes | None = None, target=None, args=(), *p_args, **p_kwargs):
    """This is just a :class:`multiprocessing.Process` factory function that sets ``address`` and ``authkey`` as proper positional parameters to the given ``target``. It is expected that this ``target`` has been properly prepared to be used with PathEx, for example, by using :func:`~.process_register`."""
    return mp.Process(target=target, args=(address, )+tuple(args), *p_args, **p_kwargs)


_T = TypeVar('_T')


class Pool:
    """This class is the analog to :class:`multiprocessing.pool.Pool` but it provides :meth:`~.apply` and :meth:`~.apply_async` methods that automatically set ``address`` and ``authkey`` as proper positional arguments."""

    def __init__(self, address, *args, **kwargs) -> None:
        self._pool = mpPool(*args, **kwargs)
        self._address = address

    def apply(self, func: Callable[..., _T], args: Iterable[Any], *a_args, **a_kwargs) -> _T:
        return self._pool.apply(func, args=(self._address,)+tuple(args),
                                *a_args, **a_kwargs)

    def apply_async(self, func: Callable[..., _T], args: Iterable[Any], *a_args, **a_kwargs) -> AsyncResult[_T]:
        return self._pool.apply_async(func, args=(self._address,)+tuple(args),
                                      *a_args, **a_kwargs)

    def __enter__(self):
        self._pool.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self._pool.__exit__(*args, **kwargs)

    def close(self):
        return self._pool.close()

    def terminate(self):
        return self._pool.terminate()

    def join(self):
        return self._pool.join()



class ProcessPoolExecutor:
    """This class is the analog to :class:`concurrent.futures.ProcessPoolExecutor` but it provides a :meth:`~.submit` method that automatically set ``address`` and ``authkey`` as proper positional arguments."""

    def __init__(self, address, *args, **kwargs) -> None:
        """"""
        self._pool = cfProcessPoolExecutor(*args, **kwargs)
        self._address = address

    def submit(self, fn: Callable[..., _T], *args: Any, **kwargs: Any) -> Future[_T]:
        return self._pool.submit(fn, *((self._address,)+args), **kwargs)

    def shutdown(self, wait: bool = ..., *, cancel_futures: bool = ...) -> None:
        return self._pool.shutdown(wait=wait, cancel_futures=cancel_futures)

    def __enter__(self):
        self._pool.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self._pool.__exit__(*args, **kwargs)
