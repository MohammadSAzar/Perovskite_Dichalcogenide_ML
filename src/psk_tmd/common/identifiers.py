from enum import Enum


class EntityPrefix(str, Enum):
    PAPER = "PPR"
    SAMPLE = "SMP"
    COMPOSITION = "CMP"
    PAIR = "PAIR"
    STRUCTURE = "STR"
    MAPPING = "MAP"


def make_sequential_id(
        prefix: EntityPrefix,
        number: int,
        width: int = 6,
    ) -> str:
    """
    Create a zero-padded internal project identifier.

    Parameters
    ----------
    prefix:
        Entity prefix.
    number:
        Positive integer identifier number.
    width:
        Number of digits used for zero-padding.

    Returns
    -------
    str
        Formatted identifier.

    Raises
    ------
    ValueError
        If number is less than 1 or width is less than 1.
    """
    if number < 1:
        raise ValueError("Identifier number must be >= 1.")

    if width < 1:
        raise ValueError("Identifier width must be >= 1.")

    return f"{prefix.value}-{number:0{width}d}"


