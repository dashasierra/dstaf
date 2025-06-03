import enum


def extend_enum(inherited_enum: enum.EnumMeta):
    """
    Class Decorator to Extend Enumerators
    """

    def wrapper(added_enum: enum.EnumMeta) -> enum.EnumMeta:
        joined = {}
        for item in inherited_enum:
            joined[item.name] = item.value
        for item in added_enum:
            joined[item.name] = item.value
        return enum.Enum(added_enum.__name__, joined)

    return wrapper


class Alignment(str, enum.Enum):
    """
    Base Alignment enumerator
    """

    LEFT = 1
    CENTRE = 2
    RIGHT = 4
    TOP = 8
    BOTTOM = 16
    JUSTIFY = 32


class VerticalAlignment(str, enum.Enum):
    """
    Vertical Alignment Enumerator
    """

    TOP = Alignment.TOP
    CENTRE = Alignment.CENTRE
    BOTTOM = Alignment.BOTTOM


class HorizontalAlignment(str, enum.Enum):
    """
    Horizontal Alignment Enumerator

      Create Example:
        align = HorizontalAlignment.LEFT

      Check by:
        if align.value == Alignment.LEFT
        ...
    """

    LEFT = Alignment.LEFT
    CENTRE = Alignment.CENTRE
    RIGHT = Alignment.RIGHT


@extend_enum(HorizontalAlignment)
class TextAlignment(str, enum.Enum):
    """
    Extended Horizontal Alignment Enumerator
    Also Contains JUSTIFY for Text alignment
    """

    JUSTIFY = Alignment.JUSTIFY
