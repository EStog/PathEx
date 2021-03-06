from __future__ import annotations

import threading

from pathex.adts.concurrency.counted_condition import CountedCondition
from pathex.expressions.expression import Expression
from pathex.machines.decomposers.decomposer import DecomposerMatch
from pathex.managing.manager import Manager
from pathex.managing.mixins import LogbookMixin

__all__ = ['Synchronizer']


class LabelInfo(CountedCondition):
    def __init__(self, lock):
        super().__init__(lock)
        self._requests = 0
        self._permits = 0

    def get_requests(self):
        with self:
            return self._requests

    def get_permits(self):
        with self:
            return self._permits

    def inc_requests(self):
        with self:
            self._requests += 1

    def inc_permits(self):
        with self:
            self._permits += 1

    def notify(self) -> None:
        super().notify()
        self._permits += 1


class Synchronizer(Manager, LogbookMixin):
    """This class is a manager that controls the execution of its registered threads.

    Example using :meth:`match`::

        >>> from concurrent.futures import ThreadPoolExecutor
        >>> from pathex import Synchronizer, Concatenation as C

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
        >>> assert set(consumed) == {0, 1, 2, 3}
        >>> assert sync.requests('Pi') == sync.permits('Pf') == sync.requests('Ci') == sync.permits('Cf') == 4
        >>> assert sync.permits('WrongTag') == sync.requests('WrongTag') == 0

    Example using :meth:`region` as a context manager::

        >>> from concurrent.futures import ThreadPoolExecutor
        >>> from pathex import Synchronizer, Tag

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

        >>> from pathex.adts.util import SET_OF_TUPLES
        >>> allowed_paths = exp.get_language(SET_OF_TUPLES)

        >>> assert tuple(shared_list) in allowed_paths

    Example using :meth:`region` as a function decorator::

        >>> a, b, c = Tag.anonym(3)

        >>> exp = ( a + (b|c) )+2

        >>> shared_list = []

        >>> sync = Synchronizer(exp)

        >>> @sync.region(a)
        ... def func_a():
        ...     shared_list.append(a.enter)
        ...     # print('Func a')
        ...     shared_list.append(a.exit)

        >>> @sync.region(b)
        ... def func_b():
        ...     shared_list.append(b.enter)
        ...     # print('Func b')
        ...     shared_list.append(b.exit)

        >>> def func_c():
        ...     shared_list.append(c.enter)
        ...     # print('Func c')
        ...     shared_list.append(c.exit)

        >>> # Another way of applying decoration
        >>> func_c = sync.region(c)(func_c)

        >>> with ThreadPoolExecutor(max_workers=4) as executor:
        ...     _ = executor.submit(func_c)
        ...     _ = executor.submit(func_a)
        ...     _ = executor.submit(func_b)
        ...     _ = executor.submit(func_a)

        >>> from pathex.adts.util import SET_OF_TUPLES
        >>> allowed_paths = exp.get_language(SET_OF_TUPLES)

        >>> assert tuple(shared_list) in allowed_paths

    Example using :meth:`region` as a method decorator::

        >>> from collections.abc import Iterable

        >>> class SharedList:
        ...     # expression and synchronizer may be defined
        ...     # outside the class if necessary. Here, it are
        ...     # inside the class just for convenience.
        ...     a, b, c = Tag.anonym(3)
        ...     exp = ( a + (b|c) )+2
        ...     sync = Synchronizer(exp)
        ...
        ...     def __init__(self):
        ...         self._l = []
        ...
        ...     def __iter__(self):
        ...         return iter(self._l)
        ...
        ...     @sync.region(a)
        ...     def func_a(self):
        ...         self._l.append(self.a.enter)
        ...         # print('Func a')
        ...         self._l.append(self.a.exit)
        ...
        ...     @sync.region(b)
        ...     def func_b(self):
        ...         self._l.append(self.b.enter)
        ...         # print('Func b')
        ...         self._l.append(self.b.exit)
        ...
        ...     def func_c(self):
        ...         self._l.append(self.c.enter)
        ...         # print('Func c')
        ...         self._l.append(self.c.exit)
        ...
        ...     # Another way of applying decoration
        ...     func_c = sync.region(c)(func_c)

        >>> shared = SharedList()
        >>> with ThreadPoolExecutor(max_workers=4) as executor:
        ...     _ = executor.submit(shared.func_c)
        ...     _ = executor.submit(shared.func_a)
        ...     _ = executor.submit(shared.func_b)
        ...     _ = executor.submit(shared.func_a)

        >>> from pathex.adts.util import SET_OF_TUPLES
        >>> allowed_paths = shared.exp.get_language(SET_OF_TUPLES)

        >>> assert tuple(shared) in allowed_paths

    Example of *readers* and *writers* threads:

        >>> from collections import deque
        >>> from concurrent.futures import ThreadPoolExecutor
        >>> from pathex import Synchronizer, Tag

        >>> writer, reader = Tag.named('writer', 'reader')

        >>> exp = (writer | reader//...)+...

        >>> sync = Synchronizer(exp)

        >>> shared_buffer = deque()

        >>> @sync.region(writer)
        ... def append(x):
        ...     shared_buffer.append(x)

        >>> @sync.region(reader)
        ... def get_top():
        ...     try:
        ...         x = shared_buffer[0]
        ...     except Exception:
        ...         return None
        ...     else:
        ...         return x

        >>> @sync.region(writer)
        ... def appendleft(x):
        ...     shared_buffer.appendleft(x)

        >>> with ThreadPoolExecutor() as executor:
        ...     _ = [executor.submit(append, 4) for _ in range(5)]
        ...     _ = [executor.submit(get_top) for _ in range(5)]
        ...     _ = [executor.submit(appendleft, 3) for _ in range(5)]

        >>> assert shared_buffer == deque([3, 3, 3, 3, 3, 4, 4, 4, 4, 4])
    """

    def __init__(self, exp: Expression,
                 decomposer: DecomposerMatch | None = None,
                 lock_class=threading.Lock):
        super().__init__(exp, decomposer)
        self._lock_class = lock_class
        self._sync_lock = lock_class()
        self._labels: dict[object, LabelInfo] = {}

    match = Manager.match
    """This method is used to wait for the availability of a single label.

    If the expression of the synchronizer is not able to generate the given object then the execution is blocked until the presence of another label in another task advances the associated expression's automata, so it can generate the label given in this method.

    The direct use of this method should be exercised with caution, because it leads to non structured code. In fact, in an object oriented design, its use should be discouraged. This method is public just because it might be usefull in a very specific and extraordinary use case where an structured approach may be too expensive, harder to design or to maintain.

    For an structured approach use the decorator :meth:`register` or the context manager :meth:`region`.

    Args:
        label (object): The label to wait for.
    """

    def _when_requested_match(self, label: object) -> object:
        self._sync_lock.acquire()  # protect the entire procedure
        label_info = self._labels.setdefault(
            label, LabelInfo(self._lock_class()))
        label_info.inc_requests()
        # print(f'requested {label}')
        return label_info

    def _when_matched(self, label: object, label_info: LabelInfo) -> None:
        # print(f'matched {label}')
        self._check_waiting_labels()
        label_info.inc_permits()
        self._sync_lock.release()

    def _when_not_matched(self, label: object, label_info: LabelInfo) -> None:
        # print(f'not_matched {label}')
        # release the procedure's protection lock in order to get blocked in the following line, so the blocking will be because this task being waiting for some other task, not because of the procedure's protection lock
        self._sync_lock.release()

        # lock.acquire in order to block.
        # lock.release must be done by another task.
        with label_info:
            label_info.wait()

    def _check_waiting_labels(self):
        while True:
            for label in self._labels:
                lock = self._labels[label]
                with lock:
                    if lock.waiting_count > 0:
                        if self._advance(label):
                            # print(f'releasing {label}')
                            lock.notify()
                            # print(f'{label} released')
                            break
            else:
                break

    def requests(self, label: object) -> int:
        with self._sync_lock:
            if label_info := self._labels.get(label):
                return label_info.get_requests()
            else:
                return 0

    def permits(self, label: object) -> int:
        with self._sync_lock:
            if label_info := self._labels.get(label):
                return label_info.get_permits()
            else:
                return 0
