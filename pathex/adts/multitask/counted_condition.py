from threading import Condition

__all__ = ['CountedCondition']


class CountedCondition(Condition):

    def __init__(self, lock):
        """
        Args:
            lock_class (Lock): This is the class of the underlying lock.
        """
        super().__init__(lock)
        self._waiting_count = 0

    @property
    def waiting_count(self):
        return self._waiting_count

    def wait(self) -> bool:
        self._waiting_count += 1
        r = super().wait()
        return r

    def notify(self, n: int = 1) -> None:
        super().notify(n)
        self._waiting_count -= n
