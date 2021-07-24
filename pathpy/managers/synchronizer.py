import threading
from contextlib import contextmanager
from enum import Enum
from functools import wraps

from pathpy.expressions.terms.letters_unions.letters_possitive_union import \
    LettersPossitiveUnion
from pathpy.generators._expressions._named_wildcard import NamedWildcard
from pathpy.generators.alternatives_generator import alts_generator
from pathpy.generators.symbols_table import SymbolsTable

from .tag import Tag

__all__ = ['Synchronizer']


class ConcurrencyType(Enum):
    THREADING = threading


class Synchronizer:
    """This class is a manager that controls the execution of its registered threads.

    >>> from pathpy import Concatenation as C, Union as U, Tag as T

    >>> writer, reader = T(), T()
    >>> sync = Synchronizer((writer | reader%...)*...)
    >>> l = []
    >>> sync.register(writer)
    ... def append(x):
    ...     l.append(x)

    >>> sync.register(reader)
    ... def last():
    ...     return l[0]

    >>> sync.register(writer)
    >>> def pop_last():
    ...     return l.pop()


    """

    def __init__(self, exp, concurrency_type: ConcurrencyType = ConcurrencyType.THREADING):
        self._sync_module = concurrency_type.value
        self._labels = {}
        self._labels_lock = self._sync_module.Lock()
        self._alternatives = set()
        self._alternatives_lock = self._sync_module.Lock()
        self._alternatives.add((exp, SymbolsTable()))

    def wait_until_allowed(self, label):
        label = LettersPossitiveUnion({label})
        with self._labels_lock:
            lock = self._labels.setdefault(label, self._sync_module.Lock())
        lock.acquire()
        if new_alternatives := self._get_new_alternatives(label):
            lock.release()
            with self._alternatives_lock:
                self._alternatives = new_alternatives
            self._release_labels()
        else:
            lock.acquire()
            lock.release()

    def _get_new_alternatives(self, label):
        def _assert_right_match(label, match, table):
            if isinstance(match, NamedWildcard):
                match = table.get_value(match)
            else:  # isinstance(match, LettersPossitiveUnion):
                return LettersPossitiveUnion({match}) == label

        new_alternatives = set()
        with self._alternatives_lock:
            for exp, table in self._alternatives:
                for head, tail, table in alts_generator(exp, table):
                    match, table = table.intersect(head, label)
                    if match is not None:
                        assert _assert_right_match(label, match, table), \
                            f'Match is {match} instead of label "{label}"'
                        new_alternatives.add((tail, table))
        return new_alternatives

    def _release_labels(self):
        with self._labels_lock:
            for label in self._labels:
                if new_alternatives := self._get_new_alternatives(label):
                    lock = self._labels[label]
                    try:
                        lock.release()
                    except RuntimeError:
                        pass
                    else:
                        with self._alternatives_lock:
                            self._alternatives = new_alternatives

    def register(self, tag: Tag, func=None):
        def wrapper(wrapped):
            @wraps(wrapped)
            def f(*args, **kwargs):
                self.wait_until_allowed(tag.enter)
                x = wrapped(*args, **kwargs)
                self.wait_until_allowed(tag.exit)
                return x
            return f

        if func is None:
            return wrapper
        else:
            return wrapper(func)

    @contextmanager
    def region(self, tag: Tag):
        self.wait_until_allowed(tag.enter)
        try:
            yield self
        finally:
            self.wait_until_allowed(tag.exit)
