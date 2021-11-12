from functools import wraps

from pathex.managing.mixins import ManagerMixin
from pathex.managing.tag import Tag

__all__ = ['Concurrent']


class Concurrent:

    def __init__(self, sync):
        self._sync = sync
        self._regions = {}

    @staticmethod
    def region(tag: Tag):

        def wrapper(func):

            @wraps(func)
            def wrapped(self, *args, **kwargs):
                return self._regions.setdefault((func, tag), ManagerMixin.region(self._sync, tag)(func))(self, *args, **kwargs)

            return wrapped

        return wrapper
