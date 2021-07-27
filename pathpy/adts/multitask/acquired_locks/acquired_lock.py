from pathpy.adts.multitask.atomics.atomic_attribute import AtomicAttribute
from .pseudo_acquired_lock import PseudoAcquiredLock


class AcquiredLock(PseudoAcquiredLock):
    """This class represents a lock which is created locked and only makes a ``release`` operation if some ``acquire`` operation is waiting for a ``release`` operation.

    Instances of this class are concurrent-safe. For a concurrent-unsafe version see class `PseudoAcquiredLock`. `AcquiredLock` only differs from PseudoAcquiredLock in that the change in state is protected from concurrency.

    >>> from threading import Lock, Thread
    >>> lock = AcquiredLock(Lock)
    >>> assert lock.acquire(blocking=False) == False
    >>> assert lock.waiting == False

    >>> def f():
    ...     lock.acquire()
    ...     print('Ok!')

    >>> def g():
    ...     assert lock.waiting == True
    ...     lock.release()

    >>> t = Thread(target=f)
    >>> t.start()
    >>> Thread(target=g).start()
    >>> t.join()
    Ok!

    >>> try:
    ...     lock.release()
    ... except RuntimeError:
    ...     pass # Right!
    ... else:
    ...     print('Wrong!')
    """

    _waiting = AtomicAttribute(lock_class='_lock_class', default=False)

    def __init__(self, lock_class):
        self._lock_class = lock_class
        super().__init__(lock_class)
