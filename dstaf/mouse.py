"""
Mouse Actions
"""

import platform
from abc import ABC
from enum import Enum, EnumType


class _MouseEvent(ABC):

    class Click(Enum):
        """
        Default Click Enumerator. If this is kept, the
        inheriting event will fail.
        """

        NONE = -9

    class ClickType(Enum):
        """
        Type of mouse click
        """

        NONE = 0.0
        SINGLE = 1.0
        DOUBLE = 2.0
        TRIPLE = 4.0
        HOLD = 0.5
        RELEASE = 0.25

    def get_mouse_button(
        self, key_value: int, ignore_errors: bool = None
    ) -> [ClickType, Click]:
        """
        Convert key value to a standardised click type
        """
        if not isinstance(ignore_errors, bool):
            ignore_errors = self._ignore_errors
        for click_type in self.ClickType:
            if key_value in [key.value * click_type.value for key in self.Click]:
                return click_type, self.Click(key_value)
            if not ignore_errors:
                raise ValueError(
                    f"The mouse button value '{key_value}' is not a known mouse button type"
                )
            return self.ClickType.NONE, self.Click.NONE

    def get_types(self) -> EnumType:
        """
        Return the Click Enumerator for this class
        """
        return self.Click

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, "Click"):
            message = f"Click(Enum) not specified in {cls.__name__}"
            raise NotImplementedError(message)
        if not isinstance(cls.Click, EnumType):
            # The Click class should be an enumerator
            raise TypeError(f"{cls.__name__}.Click is not of type Enum")
        if "none" not in cls.Click.__dict__:
            raise NameError(f"{cls.__name__}.Click.none must exist")
        if cls.Click.NONE.value == -9:
            # This means the default Click class is present, so:
            message = f"Click(Enum) not specified in {cls.__name__}"
            raise NotImplementedError(message)
        if "ignore_errors" in kwargs:
            cls._ignore_errors = kwargs["ignore_errors"]
        else:
            cls._ignore_errors = False


class _WindowsMouseEvent(_MouseEvent):

    class Click(Enum):
        """
        Mouse Click Integer Values for Windows Terminals
        """

        NONE = 0
        LEFT = 1
        RIGHT = 2
        MIDDLE = 4
        SCROLL_UP = 7864320
        SCROLL_DOWN = 4287102976


class _CursesMouseEvent(_MouseEvent):

    class Click(Enum):
        """
        Mouse Click Integer Values for Curses
        """

        NONE = 0
        LEFT = 4
        RIGHT = 4096
        MIDDLE = 128
        SCROLL_UP = 65536
        SCROLL_DOWN = 2097152


if platform.system().lower() == "Windows":
    Event = _WindowsMouseEvent
else:
    Event = _CursesMouseEvent
