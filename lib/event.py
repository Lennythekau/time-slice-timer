from collections.abc import Callable
from typing import Any, Self


class _BaseEvent:
    def __init__(self) -> None:
        self._listeners: list[Callable[..., Any]] = []

    def __iadd__(self, listener: Callable[..., Any]) -> Self:
        self._listeners.append(listener)
        return self

    def __isub__(self, listener: Callable[..., Any]) -> Self:
        try:
            self._listeners.remove(listener)
        except ValueError:
            pass
        return self


# We need both an Event0 and an Event1 class
# I tried making nullary event works by having just 1 event class (Event[TArg]), and setting the default to be Never
# However, this wasn't compatible with unary functions that didn't have a type annotation on them
# This was an issue, since in a previous version, I had used None as the default, and so I had many event handlers
# which took in None, with parameter _.
# Although this is more verbose, it's clearer, and safer.


class Event0(_BaseEvent):
    """Nullary event (doesn't take in any arguments)."""

    def __iadd__(self, listener: Callable[[], Any]):
        return super().__iadd__(listener)

    def __isub__(self, listener: Callable[[], Any]):
        return super().__isub__(listener)

    def __call__(self) -> None:
        for listener in list(self._listeners):
            listener()


class Event[TArg](_BaseEvent):
    """Unary event (takes in exactly one argument)."""

    def __iadd__(self, listener: Callable[[TArg], Any]):
        return super().__iadd__(listener)

    def __isub__(self, listener: Callable[[TArg], Any]):
        return super().__isub__(listener)

    def __call__(self: Event[TArg], arg: TArg) -> None:
        for listener in list(self._listeners):
            listener(arg)
