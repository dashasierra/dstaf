import platform
from abc import ABC
from enum import Enum, EnumType


class _MouseEvent(ABC):

    class Click(Enum):
        none = -9

    class ClickType(Enum):
        none = 0.0
        single = 1.0
        double = 2.0
        triple = 4.0
        hold = 0.5
        release = 0.25

    def get_mouse_button(
        self, key_value: int, ignore_errors: bool = None
    ) -> [ClickType, Click]:
        if not isinstance(ignore_errors, bool):
            ignore_errors = self._ignore_errors
        for click_type in self.ClickType:
            if key_value in [key.value * click_type.value for key in self.Click]:
                return click_type, self.Click(key_value)
            if not ignore_errors:
                raise ValueError(
                    f"The mouse button value '{key_value}' is not a known mouse button type"
                )
            return self.ClickType.none, self.Click.none

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, "Click"):
            raise NotImplementedError(
                f"Click(Enum) not specified in {
                    cls.__name__}"
            )
        if not isinstance(cls.Click, EnumType):
            # The Click class should be an enumerator
            raise TypeError(f"{cls.__name__}.Click is not of type Enum")
        if "none" not in cls.Click.__dict__.keys():
            raise NameError(f"{cls.__name__}.Click.none must exist")
        if cls.Click.none.value == -9:
            # This means the default Click class is present, so:
            raise NotImplementedError(
                f"Click(Enum) not specified in {
                    cls.__name__}"
            )
        if "ignore_errors" in kwargs.keys():
            cls._ignore_errors = kwargs["ignore_errors"]
        else:
            cls._ignore_errors = False


class _WindowsMouseEvent(_MouseEvent):

    class Click(Enum):
        """
        Mouse Click Integer Values for Windows Terminals
        """

        none = 0
        left = 1
        right = 2
        middle = 4
        scroll_up = 7864320
        scroll_down = 4287102976


class _CursesMouseEvent(_MouseEvent):

    class Click(Enum):
        """
        Mouse Click Integer Values for Curses
        """

        none = 0
        left = 4
        right = 4096
        middle = 128
        scroll_up = 65536
        scroll_down = 2097152


if platform.system().lower() == "Windows":
    Event = _WindowsMouseEvent
else:
    Event = _CursesMouseEvent
