import pytest

from psk_tmd.corpus.xml_text import extract_xml_text, get_local_tag


# ---------------------------------------------------------------------------
# LOCAL XML TAG
# ---------------------------------------------------------------------------
def test_get_local_tag_without_namespace():
    assert get_local_tag("sec") == "sec"


def test_get_local_tag_with_namespace():
    assert (
        get_local_tag(
            "{http://example.org/jats}sec"
        )
        == "sec"
    )


# ---------------------------------------------------------------------------
# EXTRACT XML TEXT
# ---------------------------------------------------------------------------
def test_extract_xml_text(
    tmp_path,
):
    xml_path = tmp_path / "test.xml"

    xml_content = """
    <article>
        <body>
            <sec>
                <title>Experimental</title>
                <p>
                    The catalyst was prepared
                    hydrothermally.
                </p>
            </sec>

            <sec>
                <title>Photocatalytic mechanism</title>
                <p>
                    A direct Z-scheme mechanism
                    was proposed.
                </p>
            </sec>
        </body>
    </article>
    """

    xml_path.write_text(
        xml_content,
        encoding="utf-8",
    )

    result = extract_xml_text(
        xml_path
    )

    assert result.source_format == "xml"

    assert (
        result.extraction_method
        == "xml_elementtree"
    )

    assert result.page_count == 0
    assert result.pages == []

    assert len(result.sections) == 2

    assert (
        result.sections[0].title
        == "Experimental"
    )

    assert (
        "prepared hydrothermally"
        in result.sections[0].text
    )

    assert (
        result.sections[1].title
        == "Photocatalytic mechanism"
    )

    assert (
        "direct Z-scheme mechanism"
        in result.sections[1].text
    )

    assert (
        "Photocatalytic mechanism"
        in result.full_text
    )


# ---------------------------------------------------------------------------
# NAMESPACED XML
# ---------------------------------------------------------------------------
def test_extract_namespaced_xml(
    tmp_path,
):
    xml_path = (
        tmp_path / "namespaced.xml"
    )

    xml_content = """
    <article xmlns="http://example.org/jats">
        <body>
            <sec>
                <title>Results</title>
                <p>
                    Charge transfer was improved.
                </p>
            </sec>
        </body>
    </article>
    """

    xml_path.write_text(
        xml_content,
        encoding="utf-8",
    )

    result = extract_xml_text(
        xml_path
    )

    assert len(result.sections) == 1

    assert (
        result.sections[0].title
        == "Results"
    )

    assert (
        "Charge transfer was improved."
        in result.sections[0].text
    )


# ---------------------------------------------------------------------------
# MISSING XML
# ---------------------------------------------------------------------------
def test_extract_xml_text_rejects_missing_file(
    tmp_path,
):
    xml_path = tmp_path / "missing.xml"

    with pytest.raises(
        FileNotFoundError
    ):
        extract_xml_text(
            xml_path
        )


# ---------------------------------------------------------------------------
# NON-XML FILE
# ---------------------------------------------------------------------------
def test_extract_xml_text_rejects_non_xml(
    tmp_path,
):
    text_path = tmp_path / "test.txt"

    text_path.write_text(
        "Not XML.",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Expected an XML file",
    ):
        extract_xml_text(
            text_path
        )


# ---------------------------------------------------------------------------
# INVALID XML
# ---------------------------------------------------------------------------
def test_extract_xml_text_rejects_invalid_xml(
    tmp_path,
):
    xml_path = tmp_path / "invalid.xml"

    xml_path.write_text(
        "<article><body>",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Could not parse XML file",
    ):
        extract_xml_text(
            xml_path
        )


