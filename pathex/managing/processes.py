from __future__ import annotations

import threading
import warnings
from functools import cached_property
from multiprocessing.managers import BaseManager as mpBaseManager
from multiprocessing.managers import BaseProxy as mpBaseProxy
from multiprocessing.managers import SyncManager as mpSyncManager
from typing import Callable, Generic, Hashable, Optional, TypeVar

from pathex.expressions.expression import Expression
from pathex.machines.decomposers.decomposer import DecomposerMatch
from pathex.managing.manager import Manager
from pathex.managing.mixins import LogbookMixin, ManagerMixin
from pathex.managing.synchronizer import Synchronizer

__all__ = ['get_synchronizer']

Address = tuple[str, int]


class ThreadSynchronizerProxy(mpBaseProxy, ManagerMixin, LogbookMixin):
    """This class represents is a :class:`proxy <multiprocessing.managers.BaseProxy>` to a :class:`~.Synchronizer` object."""

    _exposed_ = ['match', 'region', 'requests', 'permits']

    region = Manager.region

    def match(self, label: object) -> object:
        return self._callmethod('match', (label,))

    def requests(self, label: object) -> int:
        return self._callmethod('requests', (label,))

    def permits(self, label: object) -> int:
        return self._callmethod('permits', (label,))


_T = TypeVar('_T', bound=mpBaseManager)


class ProcessSynchronizer(Generic[_T], ManagerMixin, LogbookMixin):
    def __init__(self, address: Optional[Address], authkey, manager_class: type[_T]):
        self._address = address
        self._authkey = authkey
        self._manager_class = manager_class

    def get_mp_manager(self) -> _T:
        raise RuntimeError('No multiprocessing manager defined')

    @cached_property
    def _synchronizer(self):
        class ProcessManager(self._manager_class):
            get_synchronizer: Callable[[], ThreadSynchronizerProxy]

        ProcessManager.register(typeid='get_synchronizer',
                                proxytype=ThreadSynchronizerProxy)
        manager = ProcessManager(address=self._address, authkey=self._authkey)
        manager.connect()
        return manager.get_synchronizer()

    region = Manager.region

    def match(self, label: Hashable) -> object:
        return self._synchronizer.match(label)

    def requests(self, label: object) -> int:
        return self._synchronizer.requests(label)

    def permits(self, label: object) -> int:
        return self._synchronizer.permits(label)


def get_synchronizer(exp: Expression,
                     decomposer: Optional[DecomposerMatch] = None,
                     lock_class=threading.Lock,
                     address: Optional[Address] = None, authkey=None,
                     manager_class: type[_T] = mpSyncManager,
                     module_name: Optional[str] = None, warn=False,
                     ensure_clean_call=False) -> ProcessSynchronizer[_T]:

    if module_name is None or module_name == '__main__':
        process_synchronizer = ProcessSynchronizer(address, authkey, manager_class)

        class ProcessManager(manager_class):
            get_synchronizer: Callable[[], ThreadSynchronizerProxy]

        synchronizer = Synchronizer(exp, decomposer, lock_class)

        ProcessManager.register(typeid='get_synchronizer',
                                proxytype=ThreadSynchronizerProxy,
                                callable=lambda: synchronizer)
        manager = ProcessManager(address=address, authkey=authkey)
        manager.start()
        process_synchronizer.get_mp_manager = lambda: manager
        process_synchronizer._address = manager.address
    else:
        if address is None:
            msg = 'address should not be None in a child process. Specify an explicit address if using "spawn" or "forkserver" start methods'
            if ensure_clean_call:
                raise RuntimeError(msg)
            elif warn:
                warnings.warn(msg, RuntimeWarning)
        if authkey is None and warn:
            warnings.warn(
                'authkey is None but it must be specified explicitly when using "spawn" or "forkserver" start methods', RuntimeWarning)
        process_synchronizer = ProcessSynchronizer(address, authkey, manager_class)

    return process_synchronizer
