from abc import ABC, abstractmethod
from enum import Enum
import os

class Event(ABC):
    """
    All Events
    """

    @property
    @abstractmethod
    def system(self):
        """Derived classes must define this property."""
        raise NotImplementedError

class InputEvent(Event):
    """
    User Input Event
    """
    @property
    @abstractmethod
    def system(self):
        """Derived classes must define this property."""
        raise NotImplementedError

class _CursesClickType(Enum):
    """
    Curses Click Type Event
    """
    name="Curses"

class _Win32ClickType(Enum):
    """
    Windows Click Type Event
    """
    name="NT"

ClickType = _Win32ClickType if os.name.lower() == "nt" else _CursesClickType

class MouseEvent(InputEvent):

    system = 5

    def __init__(self,
                 position: tuple,
                 button: int,
                 ):
        self.x, self.y = position
        self.button = button
