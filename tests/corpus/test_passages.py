from psk_tmd.corpus.document import (
    DocumentBlock,
    DocumentPage,
    DocumentSection,
    DocumentTextResult,
)
from psk_tmd.corpus.passages import (
    RelevantPassage,
    find_matched_terms,
    select_relevant_passages,
    split_into_paragraphs,
    PASSAGE_KEYWORDS,
    PassageCategory,
    find_matched_terms,
)
from psk_tmd.common.constants import (
    PaperSectionRole,
)


# ---------------------------------------------------------------------------
# SPLIT TEXT INTO PARAGRAPHS
# ---------------------------------------------------------------------------
def test_split_into_paragraphs():
    text = (
        "First paragraph.\n"
        "\n"
        "Second paragraph."
    )

    paragraphs = split_into_paragraphs(
        text
    )

    assert paragraphs == [
        "First paragraph.",
        "Second paragraph.",
    ]


# ---------------------------------------------------------------------------
# FIND MATCHED TERMS
# ---------------------------------------------------------------------------
def test_find_matched_terms_case_insensitive():
    matched = find_matched_terms(
        "A Z-scheme mechanism was proposed.",
        (
            "z-scheme",
            "type-ii",
        ),
    )

    assert matched == [
        "z-scheme",
    ]


def test_mott_schottky_does_not_match_schottky():
    matched = find_matched_terms(
        "Mott-Schottky plots were measured.",
        (
            "mott-schottky",
            "schottky",
        ),
    )

    assert matched == [
        "mott-schottky",
    ]


# ---------------------------------------------------------------------------
# PDF PASSAGE SELECTION
# ---------------------------------------------------------------------------
def test_select_relevant_passages_from_pdf():
    document = DocumentTextResult(
        pages=[
            DocumentPage(
                page_number=1,
                text=(
                    "The material was synthesized "
                    "hydrothermally.\n"
                    "A direct Z-scheme mechanism "
                    "was proposed."
                ),
            ),
        ],
        sections=[],
        full_text=(
            "The material was synthesized "
            "hydrothermally. "
            "A direct Z-scheme mechanism "
            "was proposed."
        ),
        page_count=1,
        source_format="pdf",
        extraction_method="pymupdf",
    )

    passages = (
        select_relevant_passages(
            document
        )
    )

    mechanism_passages = [
        passage
        for passage in passages
        if (
            passage.category
            == PassageCategory.MECHANISM
        )
    ]

    synthesis_passages = [
        passage
        for passage in passages
        if (
            passage.category
            == PassageCategory.SYNTHESIS
        )
    ]

    assert len(
        mechanism_passages
    ) == 1

    assert len(
        synthesis_passages
    ) == 1

    assert (
        mechanism_passages[0].page_number
        == 1
    )

    assert (
        "z-scheme"
        in mechanism_passages[0].matched_terms
    )


# ---------------------------------------------------------------------------
# XML PASSAGE SELECTION
# ---------------------------------------------------------------------------
def test_select_relevant_passages_from_xml():
    document = DocumentTextResult(
        pages=[],
        sections=[
            DocumentSection(
                section_index=1,
                title=(
                    "Photocatalytic mechanism"
                ),
                text=(
                    "Electrons migrate across "
                    "the heterojunction interface."
                ),
            ),
        ],
        full_text=(
            "Photocatalytic mechanism. "
            "Electrons migrate across "
            "the heterojunction interface."
        ),
        page_count=0,
        source_format="xml",
        extraction_method="xml_elementtree",
    )

    passages = (
        select_relevant_passages(
            document
        )
    )

    categories = {
        passage.category
        for passage in passages
    }

    assert (
        PassageCategory.MECHANISM
        in categories
    )

    assert (
        PassageCategory.PHOTOCATALYTIC_TEST
        in categories
    )

    assert (
        passages[0].section_title
        == "Photocatalytic mechanism"
    )


# ---------------------------------------------------------------------------
# MULTIPLE CATEGORIES
# ---------------------------------------------------------------------------
def test_passage_can_match_multiple_categories():
    document = DocumentTextResult(
        pages=[
            DocumentPage(
                page_number=3,
                text=(
                    "The photocatalytic mechanism "
                    "was evaluated under visible light."
                ),
            ),
        ],
        sections=[],
        full_text=(
            "The photocatalytic mechanism "
            "was evaluated under visible light."
        ),
        page_count=1,
        source_format="pdf",
        extraction_method="pymupdf",
    )

    passages = (
        select_relevant_passages(
            document
        )
    )

    categories = {
        passage.category
        for passage in passages
    }

    assert (
        PassageCategory.MECHANISM
        in categories
    )

    assert (
        PassageCategory.PHOTOCATALYTIC_TEST
        in categories
    )


# ---------------------------------------------------------------------------
# IRRELEVANT TEXT
# ---------------------------------------------------------------------------
def test_irrelevant_text_produces_no_passages():
    document = DocumentTextResult(
        pages=[
            DocumentPage(
                page_number=1,
                text=(
                    "The authors thank the university "
                    "for financial support."
                ),
            ),
        ],
        sections=[],
        full_text=(
            "The authors thank the university "
            "for financial support."
        ),
        page_count=1,
        source_format="pdf",
        extraction_method="pymupdf",
    )

    passages = (
        select_relevant_passages(
            document
        )
    )

    assert passages == []


# ---------------------------------------------------------------------------
# KEYWORD BOUNDARIES
# ---------------------------------------------------------------------------
def test_type_i_does_not_match_type_iv():
    matched = find_matched_terms(
        "The adsorption isotherm is type IV.",
        (
            "type i",
        ),
    )

    assert matched == []


def test_type_i_matches_type_i():
    matched = find_matched_terms(
        "A Type I heterojunction was proposed.",
        (
            "type i",
        ),
    )

    assert matched == [
        "type i",
    ]


# ---------------------------------------------------------------------------
# REFERENCE EXCLUSION
# ---------------------------------------------------------------------------
def test_pdf_references_are_excluded():
    document = DocumentTextResult(
        pages=[
            DocumentPage(
                page_number=1,
                text=(
                    "A Z-scheme mechanism "
                    "was proposed."
                ),
                blocks=[
                    DocumentBlock(
                        block_index=1,
                        text=(
                            "A Z-scheme mechanism "
                            "was proposed."
                        ),
                    ),
                ],
            ),
            DocumentPage(
                page_number=2,
                text=(
                    "References\n"
                    "A cited Z-scheme paper."
                ),
                blocks=[
                    DocumentBlock(
                        block_index=1,
                        text="References",
                    ),
                    DocumentBlock(
                        block_index=2,
                        text=(
                            "A cited Z-scheme paper."
                        ),
                    ),
                ],
            ),
        ],
        sections=[],
        full_text=(
            "A Z-scheme mechanism was proposed. "
            "References A cited Z-scheme paper."
        ),
        page_count=2,
        source_format="pdf",
        extraction_method="pymupdf_blocks",
    )

    passages = select_relevant_passages(
        document
    )

    assert passages

    assert all(
        passage.page_number == 1
        for passage in passages
    )


# ---------------------------------------------------------------------------
# PDF PASSAGES CARRY SECTION ROLE
# ---------------------------------------------------------------------------
def test_pdf_passages_carry_section_role():
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
                            "Previous XPS studies "
                            "reported charge transfer."
                        ),
                    ),
                    DocumentBlock(
                        block_index=3,
                        text=(
                            "3. Results and discussion"
                        ),
                    ),
                    DocumentBlock(
                        block_index=4,
                        text=(
                            "The photocurrent response "
                            "was higher for the "
                            "heterostructure."
                        ),
                    ),
                    DocumentBlock(
                        block_index=5,
                        text=(
                            "3.6. Photocatalytic "
                            "mechanism analysis"
                        ),
                    ),
                    DocumentBlock(
                        block_index=6,
                        text=(
                            "Radical trapping "
                            "supported the Z-scheme "
                            "mechanism."
                        ),
                    ),
                ],
            ),
        ],
        sections=[],
        full_text="",
        page_count=1,
        source_format="pdf",
        extraction_method=(
            "pymupdf_blocks"
        ),
    )

    passages = select_relevant_passages(
        document
    )

    introduction_passages = [
        passage
        for passage in passages
        if "Previous XPS" in passage.text
    ]

    assert introduction_passages

    assert all(
        passage.section_role
        == PaperSectionRole.INTRODUCTION
        for passage in introduction_passages
    )

    results_passages = [
        passage
        for passage in passages
        if "photocurrent response"
        in passage.text
    ]

    assert results_passages

    assert all(
        passage.section_role
        == PaperSectionRole.RESULTS
        for passage in results_passages
    )

    mechanism_passages = [
        passage
        for passage in passages
        if "Radical trapping"
        in passage.text
    ]

    assert mechanism_passages

    assert all(
        passage.section_role
        == PaperSectionRole.MECHANISM
        for passage in mechanism_passages
    )


# ---------------------------------------------------------------------------
# REFERENCE PASSAGES ARE EXCLUDED
# ---------------------------------------------------------------------------
def test_reference_passages_are_excluded():
    document = DocumentTextResult(
        pages=[
            DocumentPage(
                page_number=1,
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
                            "A Z-scheme mechanism "
                            "was proposed."
                        ),
                    ),
                    DocumentBlock(
                        block_index=3,
                        text="References",
                    ),
                    DocumentBlock(
                        block_index=4,
                        text=(
                            "A cited Z-scheme "
                            "heterostructure paper."
                        ),
                    ),
                ],
            ),
        ],
        sections=[],
        full_text="",
        page_count=1,
        source_format="pdf",
        extraction_method=(
            "pymupdf_blocks"
        ),
    )

    passages = select_relevant_passages(
        document
    )

    assert passages

    assert all(
        "cited Z-scheme"
        not in passage.text
        for passage in passages
    )


# ---------------------------------------------------------------------------
# XML PASSAGES CARRY SECTION ROLE
# ---------------------------------------------------------------------------
def test_xml_passages_carry_section_role():
    document = DocumentTextResult(
        pages=[],
        sections=[
            DocumentSection(
                section_index=1,
                title="Introduction",
                text=(
                    "Previous XPS studies "
                    "reported charge transfer."
                ),
            ),
            DocumentSection(
                section_index=2,
                title=(
                    "Possible photocatalytic "
                    "mechanism"
                ),
                text=(
                    "Radical trapping supported "
                    "the Z-scheme mechanism."
                ),
            ),
        ],
        full_text="",
        page_count=0,
        source_format="xml",
        extraction_method="xml",
    )

    passages = select_relevant_passages(
        document
    )

    introduction_passages = [
        passage
        for passage in passages
        if "Previous XPS" in passage.text
    ]

    assert introduction_passages

    assert all(
        passage.section_role
        == PaperSectionRole.INTRODUCTION
        for passage in introduction_passages
    )

    mechanism_passages = [
        passage
        for passage in passages
        if "Radical trapping"
        in passage.text
    ]

    assert mechanism_passages

    assert all(
        passage.section_role
        == PaperSectionRole.MECHANISM
        for passage in mechanism_passages
    )


# ---------------------------------------------------------------------------
# BET TYPE-III IS NOT A MECHANISM KEYWORD
# ---------------------------------------------------------------------------
def test_bet_type_iii_is_not_mechanism_keyword():
    text = (
        "The nitrogen adsorption-desorption "
        "isotherm exhibits a type III curve "
        "with a hysteresis loop."
    )

    matched_terms = find_matched_terms(
        text=text,
        keywords=PASSAGE_KEYWORDS[
            PassageCategory.MECHANISM
        ],
    )

    assert "type iii" not in matched_terms
    assert "type-iii" not in matched_terms


# ---------------------------------------------------------------------------
# REAL TYPE-III REMAINS A MECHANISM KEYWORD
# ---------------------------------------------------------------------------
def test_real_type_iii_remains_mechanism_keyword():
    text = (
        "The heterojunction exhibits a "
        "Type III broken-gap band alignment."
    )

    matched_terms = find_matched_terms(
        text=text,
        keywords=PASSAGE_KEYWORDS[
            PassageCategory.MECHANISM
        ],
    )

    assert "type iii" in matched_terms

