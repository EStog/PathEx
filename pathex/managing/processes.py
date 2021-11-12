from __future__ import annotations

import warnings
from multiprocessing.managers import BaseManager as mpBaseManager
from multiprocessing.managers import BaseProxy as mpBaseProxy
from multiprocessing.managers import SyncManager as mpSyncManager
from typing import Optional, TypeVar

from pathex.managing.mixins import LogbookMixin, ManagerMixin
from pathex.managing.synchronizer import Synchronizer as peSynchronizer

__all__ = ['get_mp_process_manager', 'SynchronizerProxy']

Address = tuple[str, int]


class SynchronizerProxy(mpBaseProxy, ManagerMixin, LogbookMixin):
    """This class represents is a :class:`proxy <multiprocessing.managers.BaseProxy>` to a :class:`~.Synchronizer` object."""

    _exposed_ = ['match', 'region', 'requests', 'permits']

    def match(self, label: object) -> object:
        return self._callmethod('match', (label,))

    def requests(self, label: object) -> int:
        return self._callmethod('requests', (label,))

    def permits(self, label: object) -> int:
        return self._callmethod('permits', (label,))


_T = TypeVar('_T', bound=mpBaseManager)


def get_mp_process_manager(module_name: Optional[str],
                           address: Optional[Address] = None, authkey=None,
                           manager_class: type[_T] = mpSyncManager,
                           ensure_clean_call=False, warn=False):
    """Returns a ``manager_class`` according with ``module_name``. If ``module_name`` is ``__main__`` then the manager will be :meth:`started <multiprocessing.managers.BaseManager.start>` in the given address with the given authkey. If ``module_name`` is not ``__main__`` then the manager will be :meth:`connected <multiprocessing.managers.BaseManager.connect>` to the given ``address`` with the given ``authkey``.

    If ``ensure_clean`` is ``True``, a :class:`~.RuntimeError` will be raised if ``address`` is ``None``.
    If ``ensure_clean`` is ``False`` and ``warn`` is ``True`` a :class:`~.RuntimeWarning` will be emitted instead.
    If ``ensure_clean`` is ``False`` and ``warn`` is ``False`` no error or warning will be emitted.
    If ``warn`` is ``True`` and ``authkey`` is ``None``, a :class:`~.RuntimeWarning` will be emitted.
    """
    class ProcessManager(manager_class):
        Synchronizer: type[peSynchronizer]

    if module_name == '__main__':
        ProcessManager.register(typeid='Synchronizer',
                                proxytype=SynchronizerProxy,
                                callable=peSynchronizer)
        manager = ProcessManager(address=address, authkey=authkey)
        manager.start()
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

        ProcessManager.register(typeid='Synchronizer',
                                proxytype=SynchronizerProxy)
        manager = ProcessManager(address=address, authkey=authkey)
        manager.connect()

    return manager
