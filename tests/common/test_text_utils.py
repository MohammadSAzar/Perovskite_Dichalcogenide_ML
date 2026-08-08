from psk_tmd.common.text_utils import normalize_whitespace


def test_normalize_whitespace_collapses_multiple_spaces():
    text = "Z-scheme    charge   transfer"

    result = normalize_whitespace(text)

    assert result == "Z-scheme charge transfer"


def test_normalize_whitespace_removes_line_breaks_and_tabs():
    text = "PSK-TMD\nheterostructure\tphotocatalyst"

    result = normalize_whitespace(text)

    assert result == "PSK-TMD heterostructure photocatalyst"


def test_normalize_whitespace_strips_edges():
    text = "   internal electric field   "

    result = normalize_whitespace(text)

    assert result == "internal electric field"


def test_normalize_whitespace_handles_empty_string():
    assert normalize_whitespace("") == ""


def test_normalize_whitespace_handles_whitespace_only():
    assert normalize_whitespace(" \n\t ") == ""

