from collections.abc import Callable


type Listener[TArg] = Callable[[TArg], None]


class Event[TArg]:
    def __init__(self) -> None:
        self.__listeners: list[Listener[TArg]] = []

    def __iadd__(self, listener: Listener[TArg]):
        self.__listeners.append(listener)
        return self

    def __isub__(self, listener: Listener[TArg]):
        self.__listeners.remove(listener)
        return self

    def invoke(self, arg: TArg):
        for listener in list(self.__listeners):
            listener(arg)
