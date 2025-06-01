from enum import Enum


def _extend_enum(inherited_enum):
    def wrapper(added_enum):
        joined = {}
        for item in inherited_enum:
            joined[item.name] = item.value
        for item in added_enum:
            joined[item.name] = item.value
        return Enum(added_enum.__name__, joined)
    return wrapper


class Alignment(Enum):
    """
    Alignment enumerator
    """
    LEFT = 1
    CENTRE = 2
    CENTER = 2
    RIGHT = 4
    TOP = 8
    BOTTOM = 16
    JUSTIFY = 32


class VerticalAlignment(Enum):
    TOP = Alignment.TOP
    CENTRE = Alignment.CENTRE
    CENTER = Alignment.CENTRE
    BOTTOM = Alignment.BOTTOM


class HorizontalAlignment(Enum):
    LEFT = Alignment.LEFT
    CENTRE = Alignment.CENTRE
    CENTER = Alignment.CENTER
    RIGHT = Alignment.RIGHT


@_extend_enum(HorizontalAlignment)
class TextAlignment(Enum):
    JUSTIFY = Alignment.JUSTIFY
