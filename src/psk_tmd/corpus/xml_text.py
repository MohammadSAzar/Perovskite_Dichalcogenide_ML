from pathlib import Path
from xml.etree import ElementTree

from psk_tmd.common.text_utils import normalize_whitespace
from psk_tmd.corpus.document import (
    DocumentSection,
    DocumentTextResult,
)


# ---------------------------------------------------------------------------
# LOCAL XML TAG
# ---------------------------------------------------------------------------
def get_local_tag(
    tag: str,
) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]

    return tag


# ---------------------------------------------------------------------------
# ELEMENT TEXT
# ---------------------------------------------------------------------------
def get_element_text(
    element: ElementTree.Element,
) -> str:
    raw_text = " ".join(
        element.itertext()
    )

    return normalize_whitespace(
        raw_text
    )


# ---------------------------------------------------------------------------
# DIRECT SECTION TITLE
# ---------------------------------------------------------------------------
def get_section_title(
    section: ElementTree.Element,
) -> str | None:
    for child in section:
        if get_local_tag(child.tag) == "title":
            title = get_element_text(child)

            if title:
                return title

    return None


# ---------------------------------------------------------------------------
# FIND TOP-LEVEL SECTIONS
# ---------------------------------------------------------------------------
def find_top_level_sections(
    root: ElementTree.Element,
) -> list[ElementTree.Element]:
    section_tags = {
        "sec",
        "section",
    }

    sections: list[ElementTree.Element] = []

    def visit(
        element: ElementTree.Element,
        inside_section: bool,
    ) -> None:
        local_tag = get_local_tag(
            element.tag
        )

        is_section = (
            local_tag in section_tags
        )

        if is_section and not inside_section:
            sections.append(
                element
            )

        for child in element:
            visit(
                child,
                inside_section or is_section,
            )

    visit(
        root,
        False,
    )

    return sections


# ---------------------------------------------------------------------------
# EXTRACT XML TEXT
# ---------------------------------------------------------------------------
def extract_xml_text(
    path: str | Path,
) -> DocumentTextResult:
    xml_path = Path(path)

    if not xml_path.exists():
        raise FileNotFoundError(
            f"XML file does not exist: {xml_path}"
        )

    if not xml_path.is_file():
        raise ValueError(
            f"XML path is not a file: {xml_path}"
        )

    if xml_path.suffix.lower() != ".xml":
        raise ValueError(
            f"Expected an XML file, got: {xml_path.name}"
        )

    try:
        tree = ElementTree.parse(
            xml_path
        )

    except ElementTree.ParseError as exc:
        raise ValueError(
            f"Could not parse XML file: {xml_path}"
        ) from exc

    root = tree.getroot()

    full_text = get_element_text(
        root
    )

    section_elements = (
        find_top_level_sections(
            root
        )
    )

    sections: list[
        DocumentSection
    ] = []

    for section_index, element in enumerate(
        section_elements,
        start=1,
    ):
        section_text = get_element_text(
            element
        )

        sections.append(
            DocumentSection(
                section_index=section_index,
                title=get_section_title(
                    element
                ),
                text=section_text,
            )
        )

    return DocumentTextResult(
        pages=[],
        sections=sections,
        full_text=full_text,
        page_count=0,
        source_format="xml",
        extraction_method="xml_elementtree",
    )


