class PseudoAcquiredLock:
    """This class represents a lock which is created locked and only makes a ``release`` operation if some ``acquire`` operation is waiting for a ``release`` operation.

    Instances of this class are not concurrent-safe, since the waiting state is not protected in this respect. This means that calls to `acquire`, `release` and `waiting` must be protected form outside. Instances of this class are intended just as wrapper of a lock and the associated waiting state. For a concurrent-safe version see class `AcquiredLock`.

    >>> from threading import Lock, Thread
    >>> from time import sleep
    >>> lock = PseudoAcquiredLock(Lock)
    >>> assert lock.acquire(blocking=False) == False
    >>> assert lock.waiting == False

    >>> def f():
    ...     lock.acquire()
    ...     print('Ok!')

    >>> def g():
    ...     sleep(1)
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

    def __init__(self, lock_class):
        """
        Args:
            lock_class (Lock): This is the class of the underlier used locks.
        """
        self._lock = lock_class()
        self._lock.acquire()
        self._waiting = False

    @property
    def waiting(self):
        return self._waiting

    def acquire(self, *args, **kwargs):
        """Acquires the lock and sets the waiting state properly.

        Arguments are passed to the underlier lock.

        Returns:
            bool: True if acquired, False otherwise.
        """
        self._waiting = True
        r = self._lock.acquire(*args, **kwargs)
        self._waiting = False
        return r

    def release(self):
        """Release the lock only if it is not waiting.

        Raises `RuntimeError` if the lock is not waiting.
        """
        if self._waiting:
            self._lock.release()
        else:
            raise RuntimeError('There is not acquire operation waiting')
