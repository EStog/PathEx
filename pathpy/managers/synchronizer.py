from __future__ import annotations

import threading
from enum import Enum

from pathpy.adts.multitask.acquired_lock import AcquiredLock
from pathpy.managers.manager import Manager

__all__ = ['Synchronizer']


class ConcurrencyType(Enum):
    THREADING = threading


class LabelInfo(AcquiredLock):

    def __init__(self, lock_class):
        super().__init__(lock_class)
        self._requested = 0
        self._passed = 0

    def inc_requests(self):
        self._requested += 1

    def inc_permits(self):
        self._passed += 1

    def release(self):
        self.inc_permits()
        return super().release()

    @property
    def requests(self):
        return self._requested

    @property
    def permits(self):
        return self._passed


class Synchronizer(Manager):
    """This class is a manager that controls the execution of its registered threads.

    Example using method `check`:

        >>> from concurrent.futures import ThreadPoolExecutor
        >>> from pathpy import Synchronizer, Concatenation as C

        >>> # The following expression generates 'PiPfCiCf' | 'PiPfCiCfPiPfCiCf' | ...
        >>> exp = +C('Pi','Pf','Ci','Cf')
        >>> sync = Synchronizer(exp)
        >>> produced = []
        >>> consumed = []

        >>> def producer(x):
        ...     sync.match('Pi')
        ...     produced.append(x)
        ...     sync.match('Pf')

        >>> def consumer():
        ...     sync.match('Ci')
        ...     consumed.append(produced.pop())
        ...     sync.match('Cf')

        >>> with ThreadPoolExecutor(max_workers=8) as executor:
        ...     for _ in range(4):
        ...         _ = executor.submit(consumer)
        ...     for i in range(4):
        ...         _ = executor.submit(producer, i)

        >>> assert produced == []
        >>> assert consumed == [0, 1, 2, 3]
        >>> assert sync.requests('Pi') == sync.permits('Pf') == sync.requests('Ci') == sync.permits('Cf') == 4

    Example using method register:

        >>> from concurrent.futures import ThreadPoolExecutor
        >>> from pathpy import Synchronizer, Tag

        >>> a, b, c = Tag.anonym(3)

        >>> exp = ( a + (b|c) )+2

        >>> shared_list = []

        >>> sync = Synchronizer(exp)

        >>> @sync.register(a)
        ... def func_a():
        ...     shared_list.append(a.enter)
        ...     # print('Func a')
        ...     shared_list.append(a.exit)

        >>> @sync.register(b)
        ... def func_b():
        ...     shared_list.append(b.enter)
        ...     # print('Func b')
        ...     shared_list.append(b.exit)

        >>> @sync.register(c)
        ... def func_c():
        ...     shared_list.append(c.enter)
        ...     # print('Func c')
        ...     shared_list.append(c.exit)

        >>> with ThreadPoolExecutor(max_workers=4) as executor:
        ...     _ = executor.submit(func_c)
        ...     _ = executor.submit(func_a)
        ...     _ = executor.submit(func_b)
        ...     _ = executor.submit(func_a)

        >>> from pathpy.adts.collection_wrapper import get_collection_wrapper
        >>> Set = get_collection_wrapper(set, lambda s, w: s.add(tuple(w)))
        >>> allowed_paths = exp.get_language(Set)

        >>> assert tuple(shared_list) in allowed_paths

    Example using method `region`.

        >>> a, b, c = Tag.named('a', 'b', 'c')

        >>> exp = ( a + (b|c) )+2

        >>> shared_list = []

        >>> sync = Synchronizer(exp)

        >>> def func_a():
        ...     with sync.region(a):
        ...         shared_list.append(a.enter)
        ...         # print('Func a')
        ...         shared_list.append(a.exit)

        >>> def func_b():
        ...     with sync.region(b):
        ...         shared_list.append(b.enter)
        ...         # print('Func b')
        ...         shared_list.append(b.exit)

        >>> def func_c():
        ...     with sync.region(c):
        ...         shared_list.append(c.enter)
        ...         # print('Func c')
        ...         shared_list.append(c.exit)

        >>> with ThreadPoolExecutor(max_workers=4) as executor:
        ...     _ = executor.submit(func_c)
        ...     _ = executor.submit(func_a)
        ...     _ = executor.submit(func_b)
        ...     _ = executor.submit(func_a)

        >>> from pathpy.adts.collection_wrapper import get_collection_wrapper
        >>> Set = get_collection_wrapper(set, lambda s, w: s.add(tuple(w)))
        >>> allowed_paths = exp.get_language(Set)

        >>> assert tuple(shared_list) in allowed_paths
    """

    def __init__(self, exp, concurrency_type: ConcurrencyType = ConcurrencyType.THREADING):
        super().__init__(exp)
        self._sync_module = concurrency_type.value
        self._sync_lock = self._sync_module.Lock()
        self._labels: dict[object, LabelInfo] = {}

    match = Manager.match
    """This method is used to wait for the availability of a single label.

    If the expression of the synchronizer is not able to generate the given object then the execution is blocked until the presence of another label in another task advances the associated expression's automata, so it can generate the label given in this method.

    The direct use of this method should be exercised with caution, because it leads to non structured code. In fact, in an object oriented design, its use should be discouraged. This method is public just because it might be usefull in a very specific and extraordinary use case where an structured approach may be too expensive, harder to design or to maintain.

    For an structured approach use the decorator `Synchronizer.register` or the context manager `Synchronizer.region`.

    Args:
        label (object): The label to wait for.
    """

    def _when_requested_match(self, label: object) -> object:
        self._sync_lock.acquire()  # protect the entire procedure
        lock = self._labels.setdefault(
            label, LabelInfo(self._sync_module.Lock))
        lock.inc_requests()
        return lock

    def _when_matched(self, label: object, label_info: LabelInfo) -> None:
        self._check_waiting_labels()
        label_info.inc_permits()
        self._sync_lock.release()

    def _when_not_matched(self, label: object, label_info: LabelInfo) -> None:
        # release the procedure's protection lock in order to get blocked in the following line, so the blocking will be because this task being waiting for some other task, not because of the procedure's protection lock
        self._sync_lock.release()

        # lock.acquire in order to block.
        # lock.release must be done by another task.
        label_info.acquire()

    def _check_waiting_labels(self):
        while True:
            for label in self._labels:
                lock = self._labels[label]
                if lock.waiting_amount > 0:
                    if self._advance(label):
                        lock.release()
                        break
            else:
                break

    def requests(self, label: object):
        return self._labels.setdefault(label, LabelInfo(self._sync_module.Lock)).requests

    def permits(self, label: object):
        return self._labels.setdefault(label, LabelInfo(self._sync_module.Lock)).permits
