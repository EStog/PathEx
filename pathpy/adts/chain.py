from copy import copy


class Chain:
    """
    This class was necessary because of an issue with the `itertools.chain` function when using `copy.copy`.
    """

    def __init__(self, *iterables):
        self.__iterables = iterables
        self.__consume()

    def __consume(self):
        self.__current, self.__iterables = iter(
            self.__iterables[0]), self.__iterables[1:]

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                return next(self.__current)
            except StopIteration:
                if self.__iterables:
                    self.__consume()
                else:
                    raise
            else:
                break

    def __copy__(self):
        x = Chain.__new__(Chain)
        x.__iterables = copy(self.__iterables)
        x.__current = copy(self.__current)
        return x
