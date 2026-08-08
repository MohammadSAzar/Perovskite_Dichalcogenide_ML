import re


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in scientific text.

    Consecutive spaces, tabs, and line breaks are replaced by a single space.
    Leading and trailing whitespace are removed.

    Parameters
    ----------
    text:
        Raw input text.

    Returns
    -------
    str
        Text with normalized whitespace.
    """
    return re.sub(r"\s+", " ", text).strip()

