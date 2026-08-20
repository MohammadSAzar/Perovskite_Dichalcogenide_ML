from psk_tmd.common.constants import (
    PaperSectionRole,
)
from psk_tmd.corpus.document import (
    DocumentBlock,
    DocumentPage,
    DocumentTextResult,
)
from psk_tmd.corpus.sections import (
    assign_pdf_block_sections,
    classify_xml_section,
    detect_section_heading,
    strip_heading_prefix,
)


# ---------------------------------------------------------------------------
# STRIP NUMBERED HEADING PREFIX
# ---------------------------------------------------------------------------
def test_strip_numbered_heading_prefix():
    result = strip_heading_prefix(
        "3.6. Photocatalytic mechanism"
    )

    assert (
        result
        == "Photocatalytic mechanism"
    )


# ---------------------------------------------------------------------------
# DETECT INTRODUCTION HEADING
# ---------------------------------------------------------------------------
def test_detect_introduction_heading():
    result = detect_section_heading(
        "1. Introduction"
    )

    assert result is not None

    _, role = result

    assert (
        role
        == PaperSectionRole.INTRODUCTION
    )


# ---------------------------------------------------------------------------
# DETECT EXPERIMENTAL HEADING
# ---------------------------------------------------------------------------
def test_detect_experimental_heading():
    result = detect_section_heading(
        "2. Experimental"
    )

    assert result is not None

    _, role = result

    assert (
        role
        == PaperSectionRole.EXPERIMENTAL
    )


# ---------------------------------------------------------------------------
# DETECT RESULTS HEADING
# ---------------------------------------------------------------------------
def test_detect_results_heading():
    result = detect_section_heading(
        "3. Results and discussion"
    )

    assert result is not None

    _, role = result

    assert (
        role
        == PaperSectionRole.RESULTS
    )


# ---------------------------------------------------------------------------
# DETECT MECHANISM HEADING
# ---------------------------------------------------------------------------
def test_detect_mechanism_heading():
    result = detect_section_heading(
        "3.6. Photocatalytic mechanism analysis"
    )

    assert result is not None

    _, role = result

    assert (
        role
        == PaperSectionRole.MECHANISM
    )


# ---------------------------------------------------------------------------
# DETECT POSSIBLE MECHANISM HEADING
# ---------------------------------------------------------------------------
def test_detect_possible_mechanism_heading():
    result = detect_section_heading(
        "Possible photocatalytic mechanism"
    )

    assert result is not None

    _, role = result

    assert (
        role
        == PaperSectionRole.MECHANISM
    )


# ---------------------------------------------------------------------------
# DETECT CONCLUSION HEADING
# ---------------------------------------------------------------------------
def test_detect_conclusion_heading():
    result = detect_section_heading(
        "4. Conclusions"
    )

    assert result is not None

    _, role = result

    assert (
        role
        == PaperSectionRole.CONCLUSION
    )


# ---------------------------------------------------------------------------
# DETECT REFERENCES HEADING
# ---------------------------------------------------------------------------
def test_detect_references_heading():
    result = detect_section_heading(
        "References"
    )

    assert result is not None

    _, role = result

    assert (
        role
        == PaperSectionRole.REFERENCES
    )


# ---------------------------------------------------------------------------
# ORDINARY SENTENCE IS NOT HEADING
# ---------------------------------------------------------------------------
def test_ordinary_sentence_is_not_heading():
    result = detect_section_heading(
        "The photocatalytic mechanism "
        "was investigated using radical "
        "trapping experiments."
    )

    assert result is None


# ---------------------------------------------------------------------------
# ASSIGN PDF SECTION ROLES
# ---------------------------------------------------------------------------
def test_assign_pdf_block_sections():
    document = DocumentTextResult(
        pages=[
            DocumentPage(
                page_number=1,
                text="",
                blocks=[
                    DocumentBlock(
                        block_index=1,
                        text="1. Introduction",
                    ),
                    DocumentBlock(
                        block_index=2,
                        text=(
                            "Previous studies "
                            "reported XPS data."
                        ),
                    ),
                    DocumentBlock(
                        block_index=3,
                        text=(
                            "2. Experimental"
                        ),
                    ),
                    DocumentBlock(
                        block_index=4,
                        text=(
                            "The sample was "
                            "prepared hydrothermally."
                        ),
                    ),
                ],
            ),
            DocumentPage(
                page_number=2,
                text="",
                blocks=[
                    DocumentBlock(
                        block_index=1,
                        text=(
                            "3. Results and discussion"
                        ),
                    ),
                    DocumentBlock(
                        block_index=2,
                        text=(
                            "Mott-Schottky plots "
                            "were analyzed."
                        ),
                    ),
                    DocumentBlock(
                        block_index=3,
                        text=(
                            "3.6. Possible "
                            "photocatalytic mechanism"
                        ),
                    ),
                    DocumentBlock(
                        block_index=4,
                        text=(
                            "Radical trapping "
                            "supported the proposed "
                            "Z-scheme pathway."
                        ),
                    ),
                    DocumentBlock(
                        block_index=5,
                        text="References",
                    ),
                    DocumentBlock(
                        block_index=6,
                        text=(
                            "A cited Z-scheme paper."
                        ),
                    ),
                ],
            ),
        ],
        sections=[],
        full_text="",
        page_count=2,
        source_format="pdf",
        extraction_method=(
            "pymupdf_blocks"
        ),
    )

    blocks = assign_pdf_block_sections(
        document
    )

    assert (
        blocks[1].section_role
        == PaperSectionRole.INTRODUCTION
    )

    assert (
        blocks[3].section_role
        == PaperSectionRole.EXPERIMENTAL
    )

    assert (
        blocks[5].section_role
        == PaperSectionRole.RESULTS
    )

    assert (
        blocks[7].section_role
        == PaperSectionRole.MECHANISM
    )

    assert (
        blocks[9].section_role
        == PaperSectionRole.REFERENCES
    )


# ---------------------------------------------------------------------------
# CLASSIFY XML SECTION
# ---------------------------------------------------------------------------
def test_classify_xml_section():
    role = classify_xml_section(
        "Results and discussion"
    )

    assert (
        role
        == PaperSectionRole.RESULTS
    )


# ---------------------------------------------------------------------------
# UNKNOWN XML SECTION
# ---------------------------------------------------------------------------
def test_unknown_xml_section():
    role = classify_xml_section(
        "Optical properties"
    )

    assert (
        role
        == PaperSectionRole.OTHER
    )


# ---------------------------------------------------------------------------
# ASSIGN PDF SECTIONS WITHOUT BLOCKS
# ---------------------------------------------------------------------------
def test_assign_pdf_sections_falls_back_to_page_text():
    document = DocumentTextResult(
        pages=[
            DocumentPage(
                page_number=1,
                text=(
                    "A direct Z-scheme "
                    "mechanism was proposed."
                ),
                blocks=[],
            ),
        ],
        sections=[],
        full_text=(
            "A direct Z-scheme "
            "mechanism was proposed."
        ),
        page_count=1,
        source_format="pdf",
        extraction_method="pymupdf",
    )

    blocks = assign_pdf_block_sections(
        document
    )

    assert len(blocks) == 1

    assert (
        blocks[0].page_number
        == 1
    )

    assert (
        blocks[0].block_index
        == 1
    )

    assert (
        blocks[0].text
        == (
            "A direct Z-scheme "
            "mechanism was proposed."
        )
    )

    assert (
        blocks[0].section_role
        == PaperSectionRole.OTHER
    )

