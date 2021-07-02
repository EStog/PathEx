class Counter:
    def __init__(self, lock_class, value=0) -> None:
        self.__lock = lock_class()
        self.__value = value

    def __iadd__(self, value):
        with self.__lock:
            self.__value += value

    def __isub__(self, value):
        with self.__lock:
            self.__value -= value

    def __eq__(self, other) -> bool:
        t = type(other)
        if t == Counter:
            with self.__lock:
                return self.__value == other.__value
        else:
            with self.__lock:
                return self.__value == other
