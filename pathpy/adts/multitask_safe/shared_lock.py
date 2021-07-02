from functools import wraps


class _Operation:
    def __init__(self, instance, acquire, release):
        self.acquire = acquire
        self.release = release
        self.instance = instance

    def __call__(self, func=None, /, **kwargs):
        def wrapper(f):
            @wraps(f)
            def wrapped(*f_args, **f_kwargs):
                acquired = self.acquire(self.instance, **kwargs)
                if acquired:
                    x = f(*f_args, **f_kwargs)
                    self.release(self.instance)
                    return x  # <- only return when acquired is successful

            return wrapped

        if func is None:
            return wrapper
        else:
            return wrapper(func)

    def __enter__(self):
        self.acquire(self.instance)

    def __exit__(self, exc_type, exc_value, traceback):
        self.release(self.instance)
        return False


class _OperationDescriptor:
    def __init__(self, acquire, release):
        self.acquire = acquire
        self.release = release

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return _Operation(instance, self.acquire, self.release)

    def __call__(self, func=None, /, **kwargs):
        def wrapper(f):
            @wraps(f)
            def wrapped(instance, *f_args, **f_kwargs):
                acquired = self.acquire(instance, **kwargs)
                if acquired:
                    x = f(instance, *f_args, **f_kwargs)
                    self.release(instance)
                    return x  # <- only return when acquired is successful

            return wrapped

        if func is None:
            return wrapper
        else:
            return wrapper(func)

    def __enter__(self):
        raise TypeError(
            'Non bounded operation, can not be used as context manager')

    def __exit__(self):
        pass  # Just for the type checker


class SharedLock:
    """A shared (read-write) lock without a defined priority between read and write tasks.

    You may use the lock as a usual lock, but the operations of acquire and release are per
    each kind of operation. You must also specify an underlying kind of lock.

        >>> from threading import Lock

        >>> lock = SharedLock(Lock)

        >>> def append(l, x):
        ...     lock.acquire_write()
        ...     l.append(x)
        ...     lock.release_write()
        ...     return f'{x}_write'

        >>> def get_value(l, i):
        ...     lock.acquire_read()
        ...     x = l[i]
        ...     lock.release_read()
        ...     return f'{x}_read'

        >>> from concurrent.futures import ThreadPoolExecutor, as_completed

        >>> def execute(read, write):
        ...     l = [1, 2, 3]
        ...     p = {'1_read', '2_read', '4_write', '5_write'}
        ...     with ThreadPoolExecutor(max_workers=4) as executor:
        ...         f1 = executor.submit(write, l, 4)
        ...         f2 = executor.submit(read, l, 0)
        ...         f3 = executor.submit(write, l, 5)
        ...         f4 = executor.submit(read, l, 1)
        ...
        ...         for fut in as_completed([f1, f2, f3, f4]):
        ...             assert fut.result() in p

        >>> execute(get_value, append)


    You can also use `write_operation` and `read_operator` context managers:

        >>> def append(l, x):
        ...     with lock.write_operation:
        ...         l.append(x)
        ...     return f'{x}_write'

        >>> def get_value(l, i):
        ...     with lock.read_operation:
        ...         x = l[i]
        ...     return f'{x}_read'

        >>> execute(get_value, append)


    As a better alternative you can use `write_operation` and `read_operator` as decorators:

        >>> @lock.write_operation
        ... def append(l, x):
        ...     l.append(x)
        ...     return f'{x}_write'

        >>> @lock.read_operation
        ... def get_value(l, i):
        ...     x = l[i]
        ...     return f'{x}_read'

        >>> execute(get_value, append)

    Also, you can also use method annotations to achieve the same result.
    In this case the subclassing must be used

        >>> class A(SharedLock): # <-- Don't forget to subclass from SharedLock
        ...     # SharedLock.__init__ must be called implícitly if not directly inherited.
        ...
        ...     @SharedLock.write_operation
        ...     def append(self, l, x):
        ...         l.append(x)
        ...         return f'{x}_write'
        ...
        ...     @SharedLock.read_operation
        ...     def get_value(self, l, i):
        ...         x = l[i]
        ...         return f'{x}_read'

        >>> a = A(Lock)
        >>> execute(a.get_value, a.append)
    """

    def __init__(self, lock_class, *args, **kwargs):
        """Initializes the SharedLock.

        Args:
            lock_class (LockType): The underlying locks type.
            *args, **kwargs: Additional arguments to be passed to the underlying locks constructors.
        """
        # Used to ensure no priority between reads and writes
        self._read_write_lock = lock_class(*args, **kwargs)

        self._readers_counter_lock = lock_class(*args, **kwargs)
        self._current_readers = 0

        # Used to ensure interwriting and read-write mutual exclusiveness
        self._exclusion_lock = lock_class(*args, **kwargs)

        self._writers_counter_lock = lock_class(*args, **kwargs)
        self._waiting_writers = 0

    def acquire_read(self, *args, **kwargs) -> bool:
        """Acquires the lock for a read operation.

        This method should be called before any read-like operation, to specify that a new read operation is beginning.

        Args:
            *args, **kwargs: Arguments to be passed to underlying locks `acquire` methods.
        Returns:
            bool: A value telling if the acquisition was successful.
        """
        # if there are no writers waiting
        acquired = self._read_write_lock.acquire(*args, **kwargs)
        if acquired:
            # Increment the amount of running readers
            with self._readers_counter_lock:  # <- this should never indefinably block
                self._current_readers += 1
                if self._current_readers == 1:
                    # Ensure exclusivity with writers
                    acquired = self._exclusion_lock.acquire(*args, **kwargs)
                    if not acquired:  # Undo readers amount incrementing
                        self._current_readers -= 1
            self._read_write_lock.release()
        return acquired

    def release_read(self) -> None:
        """Releases the lock for a read operation.

        This method should be called after any read-like operation, to specify that a read operation is ended. Any exception raised by the underlying locks is not caught.
        """
        # Decrement the amount of running readers
        with self._readers_counter_lock:  # <- this should never indefinably block
            self._current_readers -= 1
            if self._current_readers == 0:
                # Release the exclusivity so a writer or a new group of readers can begin
                self._exclusion_lock.release()

    def acquire_write(self, *args, **kwargs):
        """Acquires the lock for a write operation.

        This method should be called before any write-like operation, to specify that a new write operation is beginning.

        Args:
            *args, **kwargs: Arguments to be passed to underlying locks `acquire` methods.
        Returns:
            bool: A value telling if the acquisition was successful.
        """
        acquired = True

        # Increment the amount of writers waiting to be executed
        with self._writers_counter_lock:  # <- this should never indefinably block
            self._waiting_writers += 1
            if self._waiting_writers == 1:
                # Ensure that no readers may begin
                acquired = self._read_write_lock.acquire(*args, **kwargs)
                if not acquired:
                    self._waiting_writers -= 1  # Undo writers amount incrementing
        if acquired:
            # Ensure exclusivity with other writers and readers
            acquired = self._exclusion_lock.acquire(*args, **kwargs)
            if acquired:
                # Decrement the amount of writers waiting to be executed
                with self._writers_counter_lock:  # <- this should never indefinably block
                    self._waiting_writers -= 1
                    if self._waiting_writers == 0:
                        # Let group of readers to begin
                        self._read_write_lock.release()
        return acquired

    def release_write(self):
        """Releases the lock for a write operation.

        This method should be called after any write-like operation, to specify that a write operation is ended. Any exception raised by the underlying locks is not caught.
        """
        # Release the exclusivity so a writer or a new group of readers can begin
        self._exclusion_lock.release()

    read_operation = _OperationDescriptor(acquire_read, release_read)
    """Decorator and context manager for a read operation.
    Any additional data to the underlying locks must be passed as keyword arguments.
    """

    write_operation = _OperationDescriptor(acquire_write, release_write)
    """Decorator and context manager for a write operation.
    Any additional data to the underlying locks must be passed as keyword arguments.
    """
