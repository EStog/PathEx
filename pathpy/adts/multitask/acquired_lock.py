from pathpy.adts.multitask.atomics.atomic_integer import AtomicInteger


class AcquiredLock:
    """This class represents a lock which is created locked and only makes a ``release`` operation if some ``acquire`` operation is waiting for a ``release`` operation.

    >>> from threading import Lock, Thread
    >>> from time import sleep
    >>> lock = AcquiredLock(Lock)
    >>> assert lock.acquire(blocking=False) == False
    >>> assert lock.waiting_amount == 0

    >>> s = ''
    >>> def f():
    ...     global s
    ...     lock.acquire()
    ...     s = 'Ok!'

    >>> def g():
    ...     assert lock.waiting_amount == 1
    ...     lock.release()

    >>> t = Thread(target=f)
    >>> t.start()
    >>> Thread(target=g).start()
    >>> t.join()
    >>> assert s == 'Ok!'

    >>> try:
    ...     lock.release()
    ... except RuntimeError:
    ...     pass # Right!
    ... else:
    ...     print('Wrong!')
    """

    def __init__(self, lock_class):
        """
        Args:
            lock_class (Lock): This is the class of the underlier used locks.
        """
        self._lock = lock_class()
        self._lock.acquire()
        self._sync_lock = lock_class()
        self._waiting_amount = AtomicInteger()

    @property
    def waiting_amount(self):
        """Just returns the amount of task waiting for a realease operation.
        This method may not reflect the actual current amount of waiting tasks.
        """
        return self._waiting_amount

    def acquire(self, *args, **kwargs):
        """Acquires the lock and sets the waiting state properly.

        Arguments are passed to the underlier lock.

        Returns:
            bool: True if acquired, False otherwise.
        """
        self._waiting_amount += 1
        r = self._lock.acquire(*args, **kwargs)
        self._waiting_amount -= 1
        return r

    def release(self):
        """Release the lock only if it is not waiting.

        Raises `RuntimeError` if the lock is not waiting.
        """
        with self._waiting_amount:
            if self._waiting_amount > 0:
                self._lock.release()
            else:
                raise RuntimeError('There is not acquire operation waiting')
