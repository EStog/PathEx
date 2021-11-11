from functools import partial, wraps

from pathex.managing.mixins import ManagerMixin
from pathex.managing.tag import Tag


class Region:
    def __init__(self, sync: ManagerMixin, tag: Tag) -> None:
        self._sync = sync
        self._tag = tag

    def __call__(self, func):

        def general_wrapper(f, *args, **kwargs):
            with self:
                return f(*args, **kwargs)

        if hasattr(func, '__get__'):
            @wraps(func)
            class WrappedMethodDescriptor:
                def __get__(self, instance, owner=None):
                    if instance is None:
                        return self
                    else:
                        return partial(general_wrapper, f=func.__get__(instance, owner))
            return WrappedMethodDescriptor()
        else:
            return wraps(func)(partial(general_wrapper, f=func))

    def __enter__(self):
        self._sync.match(self._tag.enter)
        return self._sync

    def __exit__(self, *args, **kwargs):
        self._sync.match(self._tag.exit)
