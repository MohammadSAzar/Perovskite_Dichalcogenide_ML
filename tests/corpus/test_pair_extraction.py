from psk_tmd.common.constants import (
    PaperSectionRole,
)
from psk_tmd.corpus.pair_extraction import (
    extract_pair_candidates,
    extract_psk_formulas,
    extract_tmd_formulas,
    select_primary_pair_candidate,
)
from psk_tmd.corpus.passages import (
    PassageCategory,
    RelevantPassage,
)


# ---------------------------------------------------------------------------
# MAKE PASSAGE
# ---------------------------------------------------------------------------
def make_passage(
    passage_id: str,
    text: str,
    section_role: PaperSectionRole = (
        PaperSectionRole.ABSTRACT
    ),
) -> RelevantPassage:
    return RelevantPassage(
        passage_id=passage_id,
        category=(
            PassageCategory.MATERIAL
        ),
        text=text,
        matched_terms=[],
        page_number=1,
        section_title=None,
        section_role=section_role,
    )


# ---------------------------------------------------------------------------
# EXTRACT SIMPLE PSK FORMULA
# ---------------------------------------------------------------------------
def test_extract_simple_psk_formula():
    formulas = extract_psk_formulas(
        "LaNiO3 was used as the "
        "perovskite component."
    )

    assert formulas == [
        "LaNiO3",
    ]


# ---------------------------------------------------------------------------
# EXTRACT SIMPLE TMD FORMULA
# ---------------------------------------------------------------------------
def test_extract_simple_tmd_formula():
    formulas = extract_tmd_formulas(
        "WS2 nanosheets were prepared."
    )

    assert formulas == [
        "WS2",
    ]


# ---------------------------------------------------------------------------
# REJECT INCOMPLETE TMD FORMULA
# ---------------------------------------------------------------------------
def test_reject_incomplete_tmd_formula():
    formulas = extract_tmd_formulas(
        "MoS addition increased "
        "the photocatalytic activity."
    )

    assert formulas == []


# ---------------------------------------------------------------------------
# EXTRACT COMMON PILOT PAIR
# ---------------------------------------------------------------------------
def test_extract_common_pilot_pair():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "A MoS2/CaTiO3 "
                "heterostructure was "
                "prepared."
            ),
        ),
    ]

    result = extract_pair_candidates(
        passages
    )

    assert len(
        result.pair_candidates
    ) == 1

    pair = result.pair_candidates[
        0
    ]

    assert (
        pair.psk_formula_reported
        == "CaTiO3"
    )

    assert (
        pair.tmd_formula_reported
        == "MoS2"
    )


# ---------------------------------------------------------------------------
# EXTRACT REVERSED PAIR ORDER
# ---------------------------------------------------------------------------
def test_extract_reversed_pair_order():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "The CaTiO3/WS2 "
                "heterostructure was "
                "constructed."
            ),
        ),
    ]

    result = extract_pair_candidates(
        passages
    )

    assert len(
        result.pair_candidates
    ) == 1

    pair = result.pair_candidates[
        0
    ]

    assert (
        pair.psk_formula_reported
        == "CaTiO3"
    )

    assert (
        pair.tmd_formula_reported
        == "WS2"
    )


# ---------------------------------------------------------------------------
# EXTRACT PAIR WITH LOADING
# ---------------------------------------------------------------------------
def test_extract_pair_with_loading():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "The CaTiO3(20 wt%)/WS2 "
                "heterostructure showed "
                "enhanced activity."
            ),
        ),
    ]

    result = extract_pair_candidates(
        passages
    )

    assert len(
        result.pair_candidates
    ) == 1

    assert (
        result.pair_candidates[
            0
        ].psk_formula_reported
        == "CaTiO3"
    )

    assert (
        result.pair_candidates[
            0
        ].tmd_formula_reported
        == "WS2"
    )


# ---------------------------------------------------------------------------
# PRESERVE DOPED PSK FORMULA
# ---------------------------------------------------------------------------
def test_preserve_doped_psk_formula():
    formulas = extract_psk_formulas(
        "La0.8Sr0.2FeO3 was prepared."
    )

    assert formulas == [
        "La0.8Sr0.2FeO3",
    ]


# ---------------------------------------------------------------------------
# PRESERVE MIXED-CHALCOGEN TMD FORMULA
# ---------------------------------------------------------------------------
def test_preserve_mixed_chalcogen_tmd_formula():
    formulas = extract_tmd_formulas(
        "MoS1.8Se0.2 was prepared."
    )

    assert formulas == [
        "MoS1.8Se0.2",
    ]


# ---------------------------------------------------------------------------
# PRESERVE DOPED PAIR IDENTITIES
# ---------------------------------------------------------------------------
def test_preserve_doped_pair_identities():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "The "
                "La0.8Sr0.2FeO3/"
                "MoS1.8Se0.2 "
                "heterostructure showed "
                "enhanced activity."
            ),
        ),
    ]

    result = extract_pair_candidates(
        passages
    )

    assert len(
        result.pair_candidates
    ) == 1

    pair = result.pair_candidates[
        0
    ]

    assert (
        pair.psk_formula_reported
        == "La0.8Sr0.2FeO3"
    )

    assert (
        pair.tmd_formula_reported
        == "MoS1.8Se0.2"
    )


# ---------------------------------------------------------------------------
# DO NOT CROSS-PAIR SALT WITH TMD
# ---------------------------------------------------------------------------
def test_do_not_cross_pair_salt_with_tmd():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "Photocatalytic degradation "
                "by 1%-MoS2/PbTiO3 was "
                "tested after adding NaNO3."
            ),
        ),
    ]

    result = extract_pair_candidates(
        passages
    )

    assert len(
        result.pair_candidates
    ) == 1

    pair = result.pair_candidates[
        0
    ]

    assert (
        pair.psk_formula_reported
        == "PbTiO3"
    )

    assert (
        pair.tmd_formula_reported
        == "MoS2"
    )


# ---------------------------------------------------------------------------
# DO NOT CROSS-PAIR SOURCE INCONSISTENCY
# ---------------------------------------------------------------------------
def test_do_not_cross_pair_source_inconsistency():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "The CaTiO3/WS2 "
                "heterostructure showed "
                "enhanced activity. "
                "The text also mentions "
                "LaNiO3/g-C3N4."
            ),
        ),
    ]

    result = extract_pair_candidates(
        passages
    )

    assert len(
        result.pair_candidates
    ) == 1

    pair = result.pair_candidates[
        0
    ]

    assert (
        pair.psk_formula_reported
        == "CaTiO3"
    )

    assert (
        pair.tmd_formula_reported
        == "WS2"
    )


# ---------------------------------------------------------------------------
# NO PAIR FROM UNRELATED CO-OCCURRENCE
# ---------------------------------------------------------------------------
def test_no_pair_from_unrelated_co_occurrence():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "CaTiO3 was synthesized. "
                "MoS2 was discussed as an "
                "example from prior work."
            ),
        ),
    ]

    result = extract_pair_candidates(
        passages
    )

    assert (
        result.pair_candidates
        == []
    )


# ---------------------------------------------------------------------------
# PRIMARY STUDY OUTRANKS INTRODUCTION CITATION
# ---------------------------------------------------------------------------
def test_primary_study_out_ranks_introduction_citation():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "Previous work reported "
                "MoS2/CaTiO3 "
                "heterostructures."
            ),
            section_role=(
                PaperSectionRole.INTRODUCTION
            ),
        ),
        make_passage(
            passage_id="PAS-0002",
            text=(
                "In this study, the "
                "CaTiO3/WS2 "
                "heterostructure was "
                "prepared."
            ),
            section_role=(
                PaperSectionRole.RESULTS
            ),
        ),
    ]

    result = extract_pair_candidates(
        passages
    )

    assert (
        result.pair_candidates[
            0
        ].psk_formula_reported
        == "CaTiO3"
    )

    assert (
        result.pair_candidates[
            0
        ].tmd_formula_reported
        == "WS2"
    )


# ---------------------------------------------------------------------------
# PAIR CANDIDATE PRESERVES PROVENANCE
# ---------------------------------------------------------------------------
def test_pair_candidate_preserves_provenance():
    passage = RelevantPassage(
        passage_id="PAS-0001",
        category=(
            PassageCategory.MATERIAL
        ),
        text=(
            "The CaTiO3/WS2 "
            "heterostructure was "
            "successfully constructed."
        ),
        matched_terms=[
            "heterostructure",
        ],
        page_number=5,
        section_title=(
            "Results and discussion"
        ),
        section_role=(
            PaperSectionRole.RESULTS
        ),
    )

    result = extract_pair_candidates(
        [
            passage,
        ]
    )

    pair = result.pair_candidates[
        0
    ]

    assert pair.page_number == 5

    assert (
        pair.section_title
        == "Results and discussion"
    )

    assert (
        pair.section_role
        == PaperSectionRole.RESULTS
    )

    assert (
        "CaTiO3/WS2"
        in pair.source_text
    )


# ---------------------------------------------------------------------------
# PRIMARY PAIR IS HIGHEST-RANKED CANDIDATE
# ---------------------------------------------------------------------------
def test_primary_pair_is_highest_ranked_candidate():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "Previous work reported the "
                "MoS2/CaTiO3 heterostructure."
            ),
            section_role=(
                PaperSectionRole.INTRODUCTION
            ),
        ),
        make_passage(
            passage_id="PAS-0002",
            text=(
                "In this study, the "
                "CaTiO3/WS2 heterostructure "
                "was prepared and its "
                "mechanism was investigated."
            ),
            section_role=(
                PaperSectionRole.MECHANISM
            ),
        ),
    ]

    result = extract_pair_candidates(
        passages
    )

    assert (
        result.primary_pair_candidate
        is not None
    )

    assert (
        result.primary_pair_candidate
        .psk_formula_reported
        == "CaTiO3"
    )

    assert (
        result.primary_pair_candidate
        .tmd_formula_reported
        == "WS2"
    )

    assert len(
        result.pair_candidates
    ) == 2


# ---------------------------------------------------------------------------
# NO PRIMARY PAIR WHEN NO PAIR EXISTS
# ---------------------------------------------------------------------------
def test_no_primary_pair_when_no_pair_exists():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "Pure CaTiO3 showed "
                "photocatalytic activity."
            ),
        ),
    ]

    result = extract_pair_candidates(
        passages
    )

    assert (
        result.primary_pair_candidate
        is None
    )

    assert (
        result.pair_candidates
        == []
    )

