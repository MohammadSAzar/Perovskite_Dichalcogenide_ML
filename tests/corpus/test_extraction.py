from psk_tmd.common.constants import (
    CharacterizationRole,
    EvidenceContextType,
    MechanismLabel,
    PaperSectionRole,
)
from psk_tmd.corpus.extraction import (
    CharacterizationCandidate,
    build_mechanism_evidence_candidates,
    classify_characterization_role,
    deduplicate_passages,
    extract_characterization_candidates,
    extract_mechanism_candidates,
    extract_mechanism_claims,
    find_mechanism_claim,
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
    page_number: int,
    section_role: PaperSectionRole,
) -> RelevantPassage:
    return RelevantPassage(
        passage_id=passage_id,
        category=(
            PassageCategory.MECHANISM
        ),
        text=text,
        matched_terms=[],
        page_number=page_number,
        section_title=None,
        section_role=section_role,
    )


# ---------------------------------------------------------------------------
# FIND Z-SCHEME CLAIM
# ---------------------------------------------------------------------------
def test_find_z_scheme_claim():
    result = find_mechanism_claim(
        "A direct Z-scheme mechanism "
        "was proposed."
    )

    assert result is not None

    reported, normalized = result

    assert (
        reported.lower()
        == "z-scheme"
    )

    assert (
        normalized
        == MechanismLabel.Z_SCHEME
    )


# ---------------------------------------------------------------------------
# FIND BROKEN PDF Z-SCHEME CLAIM
# ---------------------------------------------------------------------------
def test_find_broken_z_scheme_claim():
    result = find_mechanism_claim(
        "A Z- scheme electron transport "
        "mechanism was proposed."
    )

    assert result is not None

    _, normalized = result

    assert (
        normalized
        == MechanismLabel.Z_SCHEME
    )


# ---------------------------------------------------------------------------
# FIND TYPE-II CLAIM
# ---------------------------------------------------------------------------
def test_find_type_ii_claim():
    result = find_mechanism_claim(
        "A Type-II heterojunction "
        "was proposed."
    )

    assert result is not None

    _, normalized = result

    assert (
        normalized
        == MechanismLabel.TYPE_II
    )


# ---------------------------------------------------------------------------
# TYPE-IV IS NOT TYPE-I
# ---------------------------------------------------------------------------
def test_type_iv_is_not_type_i():
    result = find_mechanism_claim(
        "The adsorption isotherm "
        "was classified as type IV."
    )

    assert result is None


# ---------------------------------------------------------------------------
# BET TYPE-III IS NOT A MECHANISM
# ---------------------------------------------------------------------------
def test_bet_type_iii_is_not_mechanism():
    result = find_mechanism_claim(
        "The nitrogen adsorption-desorption "
        "isotherm displays a type III curve "
        "with a hysteresis loop."
    )

    assert result is None


# ---------------------------------------------------------------------------
# BET TYPE-II IS NOT A MECHANISM
# ---------------------------------------------------------------------------
def test_bet_type_ii_is_not_mechanism():
    result = find_mechanism_claim(
        "The BET specific surface area was "
        "calculated from a type II adsorption "
        "isotherm."
    )

    assert result is None


# ---------------------------------------------------------------------------
# REAL TYPE-II HETEROJUNCTION IS RETAINED
# ---------------------------------------------------------------------------
def test_real_type_ii_heterojunction_is_retained():
    result = find_mechanism_claim(
        "The heterojunction exhibits a "
        "Type-II band alignment that promotes "
        "interfacial charge transfer."
    )

    assert result is not None

    _, normalized = result

    assert (
        normalized
        == MechanismLabel.TYPE_II
    )


# ---------------------------------------------------------------------------
# DEDUPLICATE PASSAGES
# ---------------------------------------------------------------------------
def test_deduplicate_passages():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "A Z-scheme mechanism "
                "was proposed."
            ),
            page_number=4,
            section_role=(
                PaperSectionRole.RESULTS
            ),
        ),
        make_passage(
            passage_id="PAS-0002",
            text=(
                "A Z-scheme mechanism "
                "was proposed."
            ),
            page_number=4,
            section_role=(
                PaperSectionRole.RESULTS
            ),
        ),
    ]

    result = deduplicate_passages(
        passages
    )

    assert len(result) == 1


# ---------------------------------------------------------------------------
# INTRODUCTION CLAIM IS EXCLUDED
# ---------------------------------------------------------------------------
def test_introduction_mechanism_claim_is_excluded():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "Previous researchers proposed "
                "a Z-scheme mechanism."
            ),
            page_number=2,
            section_role=(
                PaperSectionRole.INTRODUCTION
            ),
        ),
    ]

    result = extract_mechanism_claims(
        passages
    )

    assert result == []


# ---------------------------------------------------------------------------
# MECHANISM CLAIM IS RETAINED
# ---------------------------------------------------------------------------
def test_mechanism_section_claim_is_retained():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "The Z-scheme mechanism "
                "is proposed for this "
                "heterostructure."
            ),
            page_number=9,
            section_role=(
                PaperSectionRole.MECHANISM
            ),
        ),
    ]

    result = extract_mechanism_claims(
        passages
    )

    assert len(result) == 1

    assert (
        result[0].mechanism_normalized
        == MechanismLabel.Z_SCHEME
    )

    assert (
        result[0].charge_transfer_class
        is None
    )


# ---------------------------------------------------------------------------
# MECHANISM SECTION OUTRANKS ABSTRACT
# ---------------------------------------------------------------------------
def test_mechanism_section_out_ranks_abstract():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "A Z-scheme heterostructure "
                "was fabricated."
            ),
            page_number=1,
            section_role=(
                PaperSectionRole.ABSTRACT
            ),
        ),
        make_passage(
            passage_id="PAS-0002",
            text=(
                "The proposed Z-scheme "
                "mechanism explains the "
                "electron transfer pathway."
            ),
            page_number=9,
            section_role=(
                PaperSectionRole.MECHANISM
            ),
        ),
    ]

    result = extract_mechanism_claims(
        passages
    )

    assert len(result) == 1

    assert (
        result[0].page_number
        == 9
    )


# ---------------------------------------------------------------------------
# RADICAL TRAPPING ROLE
# ---------------------------------------------------------------------------
def test_radical_trapping_is_context_dependent_mechanism_evidence():
    (
        role,
        discriminating,
        requires_context,
        required_context,
    ) = classify_characterization_role(
        evidence_type=(
            "radical_trapping"
        ),
        text=(
            "Scavenger experiments "
            "identified active radicals."
        ),
        section_role=(
            PaperSectionRole.MECHANISM
        ),
    )

    assert (
        role
        == CharacterizationRole.MECHANISM_ASSESSMENT
    )

    assert discriminating is True
    assert requires_context is True

    assert (
        EvidenceContextType.BAND_EDGES
        in required_context
    )

    assert (
        EvidenceContextType.REDOX_POTENTIALS
        in required_context
    )


# ---------------------------------------------------------------------------
# ESR ROLE
# ---------------------------------------------------------------------------
def test_esr_is_context_dependent_mechanism_evidence():
    (
        role,
        discriminating,
        requires_context,
        required_context,
    ) = classify_characterization_role(
        evidence_type="esr",
        text=(
            "ESR detected DMPO radical "
            "signals."
        ),
        section_role=(
            PaperSectionRole.RESULTS
        ),
    )

    assert (
        role
        == CharacterizationRole.MECHANISM_ASSESSMENT
    )

    assert discriminating is True
    assert requires_context is True

    assert (
        EvidenceContextType.BAND_EDGES
        in required_context
    )

    assert (
        EvidenceContextType.REDOX_POTENTIALS
        in required_context
    )


# ---------------------------------------------------------------------------
# MOTT-SCHOTTKY ROLE
# ---------------------------------------------------------------------------
def test_mott_schottky_is_band_structure():
    (
        role,
        discriminating,
        requires_context,
        required_context,
    ) = classify_characterization_role(
        evidence_type=(
            "mott_schottky"
        ),
        text=(
            "Mott-Schottky plots "
            "determined the flat-band "
            "potential."
        ),
        section_role=(
            PaperSectionRole.RESULTS
        ),
    )

    assert (
        role
        == CharacterizationRole.BAND_STRUCTURE
    )

    assert discriminating is False
    assert requires_context is False
    assert required_context == []


# ---------------------------------------------------------------------------
# BAND ALIGNMENT ROLE
# ---------------------------------------------------------------------------
def test_band_alignment_is_not_discriminating_alone():
    (
        role,
        discriminating,
        requires_context,
        required_context,
    ) = classify_characterization_role(
        evidence_type=(
            "band_alignment"
        ),
        text=(
            "The conduction band and "
            "valence band positions "
            "were determined."
        ),
        section_role=(
            PaperSectionRole.MECHANISM
        ),
    )

    assert (
        role
        == CharacterizationRole.BAND_STRUCTURE
    )

    assert discriminating is False
    assert requires_context is False
    assert required_context == []


# ---------------------------------------------------------------------------
# PL ROLE
# ---------------------------------------------------------------------------
def test_pl_is_charge_separation_support():
    (
        role,
        discriminating,
        requires_context,
        required_context,
    ) = classify_characterization_role(
        evidence_type=(
            "photoluminescence"
        ),
        text=(
            "The lower PL intensity "
            "indicates reduced "
            "electron-hole recombination."
        ),
        section_role=(
            PaperSectionRole.RESULTS
        ),
    )

    assert (
        role
        == CharacterizationRole.CHARGE_SEPARATION_SUPPORT
    )

    assert discriminating is False
    assert requires_context is False
    assert required_context == []


# ---------------------------------------------------------------------------
# PHOTOCURRENT ROLE
# ---------------------------------------------------------------------------
def test_photocurrent_is_charge_separation_support():
    (
        role,
        discriminating,
        requires_context,
        required_context,
    ) = classify_characterization_role(
        evidence_type="photocurrent",
        text=(
            "Higher photocurrent indicates "
            "improved charge separation."
        ),
        section_role=(
            PaperSectionRole.RESULTS
        ),
    )

    assert (
        role
        == CharacterizationRole.CHARGE_SEPARATION_SUPPORT
    )

    assert discriminating is False
    assert requires_context is False
    assert required_context == []


# ---------------------------------------------------------------------------
# DIRECTIONAL XPS ROLE
# ---------------------------------------------------------------------------
def test_directional_xps_can_assess_mechanism():
    (
        role,
        discriminating,
        requires_context,
        required_context,
    ) = classify_characterization_role(
        evidence_type="xps",
        text=(
            "The XPS peaks shifted to "
            "higher binding energy for "
            "component A and lower binding "
            "energy for component B, "
            "indicating electron migration "
            "from A to B."
        ),
        section_role=(
            PaperSectionRole.RESULTS
        ),
    )

    assert (
        role
        == CharacterizationRole.MECHANISM_ASSESSMENT
    )

    assert discriminating is True
    assert requires_context is True

    assert (
        EvidenceContextType.BAND_ALIGNMENT
        in required_context
    )


# ---------------------------------------------------------------------------
# ORDINARY XPS ROLE
# ---------------------------------------------------------------------------
def test_ordinary_xps_is_structural_characterization():
    (
        role,
        discriminating,
        requires_context,
        required_context,
    ) = classify_characterization_role(
        evidence_type="xps",
        text=(
            "XPS confirmed the presence "
            "of Ca, Ti, O, W and S."
        ),
        section_role=(
            PaperSectionRole.RESULTS
        ),
    )

    assert (
        role
        == CharacterizationRole.STRUCTURAL_CHARACTERIZATION
    )

    assert discriminating is False
    assert requires_context is False
    assert required_context == []


# ---------------------------------------------------------------------------
# KELVIN PROBE MECHANISM ROLE
# ---------------------------------------------------------------------------
def test_kelvin_probe_can_assess_mechanism():
    (
        role,
        discriminating,
        requires_context,
        required_context,
    ) = classify_characterization_role(
        evidence_type="kelvin_probe",
        text=(
            "Kelvin probe analysis revealed "
            "a work function difference and "
            "built-in electric field that "
            "drives electron transfer."
        ),
        section_role=(
            PaperSectionRole.MECHANISM
        ),
    )

    assert (
        role
        == CharacterizationRole.MECHANISM_ASSESSMENT
    )

    assert discriminating is True
    assert requires_context is True

    assert (
        EvidenceContextType.BAND_ALIGNMENT
        in required_context
    )


# ---------------------------------------------------------------------------
# PHOTODEPOSITION ROLE
# ---------------------------------------------------------------------------
def test_photodeposition_is_context_dependent_mechanism_evidence():
    (
        role,
        discriminating,
        requires_context,
        required_context,
    ) = classify_characterization_role(
        evidence_type="photodeposition",
        text=(
            "Photodeposition revealed the "
            "spatial location of reduction "
            "sites."
        ),
        section_role=(
            PaperSectionRole.MECHANISM
        ),
    )

    assert (
        role
        == CharacterizationRole.MECHANISM_ASSESSMENT
    )

    assert discriminating is True
    assert requires_context is True

    assert (
        EvidenceContextType.BAND_EDGES
        in required_context
    )


# ---------------------------------------------------------------------------
# INTRODUCTION CHARACTERIZATION IS EXCLUDED
# ---------------------------------------------------------------------------
def test_introduction_characterization_is_excluded():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "Previous XPS studies "
                "reported electron transfer "
                "between other materials."
            ),
            page_number=2,
            section_role=(
                PaperSectionRole.INTRODUCTION
            ),
        ),
    ]

    result = (
        extract_characterization_candidates(
            passages
        )
    )

    assert result == []


# ---------------------------------------------------------------------------
# ACTIVE SPECIES ALONE IS NOT RADICAL TRAPPING
# ---------------------------------------------------------------------------
def test_active_species_alone_is_not_radical_trapping():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "The band-edge positions "
                "allow the generation of "
                "active species such as "
                "superoxide and hydroxyl "
                "radicals."
            ),
            page_number=9,
            section_role=(
                PaperSectionRole.MECHANISM
            ),
        ),
    ]

    result = (
        extract_characterization_candidates(
            passages
        )
    )

    evidence_types = {
        candidate.evidence_type
        for candidate in result
    }

    assert (
        "radical_trapping"
        not in evidence_types
    )


# ---------------------------------------------------------------------------
# DMPO CREATES ESR NOT RADICAL TRAPPING
# ---------------------------------------------------------------------------
def test_dmpo_creates_esr_not_radical_trapping():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "ESR measurement showed "
                "strong DMPO superoxide "
                "response signals and "
                "DMPO hydroxyl signals."
            ),
            page_number=9,
            section_role=(
                PaperSectionRole.MECHANISM
            ),
        ),
    ]

    result = (
        extract_characterization_candidates(
            passages
        )
    )

    evidence_types = {
        candidate.evidence_type
        for candidate in result
    }

    assert "esr" in evidence_types

    assert (
        "radical_trapping"
        not in evidence_types
    )


# ---------------------------------------------------------------------------
# RESULTS PL IS RETAINED AS SUPPORT
# ---------------------------------------------------------------------------
def test_results_pl_is_retained_as_support():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "Photoluminescence spectra "
                "showed lower PL intensity, "
                "indicating reduced "
                "recombination."
            ),
            page_number=6,
            section_role=(
                PaperSectionRole.RESULTS
            ),
        ),
    ]

    result = (
        extract_characterization_candidates(
            passages
        )
    )

    assert len(result) == 1

    assert (
        result[0].characterization_role
        == CharacterizationRole.CHARGE_SEPARATION_SUPPORT
    )

    assert (
        result[0].mechanism_discriminating
        is False
    )


# ---------------------------------------------------------------------------
# RESULTS MOTT-SCHOTTKY IS NOT PROMOTED
# ---------------------------------------------------------------------------
def test_results_mott_schottky_is_not_mechanism_evidence():
    candidate = CharacterizationCandidate(
        evidence_type="mott_schottky",
        characterization_role=(
            CharacterizationRole.BAND_STRUCTURE
        ),
        mechanism_discriminating=False,
        requires_context=False,
        required_context=[],
        page_number=6,
        section_title=(
            "Results and discussion"
        ),
        section_role=(
            PaperSectionRole.RESULTS
        ),
        matched_terms=[
            "mott-schottky",
        ],
        source_text=(
            "Mott-Schottky analysis "
            "determined flat-band potentials."
        ),
        score=5.0,
    )

    result = (
        build_mechanism_evidence_candidates(
            [
                candidate,
            ]
        )
    )

    assert result == []


# ---------------------------------------------------------------------------
# MECHANISM BAND ALIGNMENT IS CONTEXT
# ---------------------------------------------------------------------------
def test_mechanism_band_alignment_is_context_evidence():
    candidate = CharacterizationCandidate(
        evidence_type="band_alignment",
        characterization_role=(
            CharacterizationRole.BAND_STRUCTURE
        ),
        mechanism_discriminating=False,
        requires_context=False,
        required_context=[],
        page_number=9,
        section_title=(
            "Possible photocatalytic mechanism"
        ),
        section_role=(
            PaperSectionRole.MECHANISM
        ),
        matched_terms=[
            "conduction band",
            "valence band",
        ],
        source_text=(
            "The conduction and valence "
            "band positions are used to "
            "interpret radical formation."
        ),
        score=8.0,
    )

    result = (
        build_mechanism_evidence_candidates(
            [
                candidate,
            ]
        )
    )

    assert len(result) == 1

    assert (
        result[0].mechanism_discriminating
        is False
    )


# ---------------------------------------------------------------------------
# RADICAL TRAPPING IS PROMOTED
# ---------------------------------------------------------------------------
def test_radical_trapping_is_promoted_to_mechanism_evidence():
    candidate = CharacterizationCandidate(
        evidence_type=(
            "radical_trapping"
        ),
        characterization_role=(
            CharacterizationRole.MECHANISM_ASSESSMENT
        ),
        mechanism_discriminating=True,
        requires_context=True,
        required_context=[
            EvidenceContextType.BAND_EDGES,
            EvidenceContextType.REDOX_POTENTIALS,
        ],
        page_number=9,
        section_title=(
            "Possible photocatalytic mechanism"
        ),
        section_role=(
            PaperSectionRole.MECHANISM
        ),
        matched_terms=[
            "scavenger",
        ],
        source_text=(
            "Scavenger experiments "
            "identified the dominant "
            "active species."
        ),
        score=10.0,
    )

    result = (
        build_mechanism_evidence_candidates(
            [
                candidate,
            ]
        )
    )

    assert len(result) == 1

    assert (
        result[0].mechanism_discriminating
        is True
    )

    assert (
        result[0].requires_context
        is True
    )

    assert (
        EvidenceContextType.BAND_EDGES
        in result[0].required_context
    )

    assert (
        EvidenceContextType.REDOX_POTENTIALS
        in result[0].required_context
    )


# ---------------------------------------------------------------------------
# COMPLETE EXTRACTION
# ---------------------------------------------------------------------------
def test_extract_mechanism_candidates():
    passages = [
        make_passage(
            passage_id="PAS-0001",
            text=(
                "Previous XPS studies "
                "reported a Z-scheme "
                "mechanism for other systems."
            ),
            page_number=2,
            section_role=(
                PaperSectionRole.INTRODUCTION
            ),
        ),
        make_passage(
            passage_id="PAS-0002",
            text=(
                "Mott-Schottky analysis "
                "determined the flat-band "
                "potentials."
            ),
            page_number=6,
            section_role=(
                PaperSectionRole.RESULTS
            ),
        ),
        make_passage(
            passage_id="PAS-0003",
            text=(
                "Photoluminescence showed "
                "lower recombination."
            ),
            page_number=6,
            section_role=(
                PaperSectionRole.RESULTS
            ),
        ),
        make_passage(
            passage_id="PAS-0004",
            text=(
                "The Z-scheme mechanism "
                "was proposed. Scavenger "
                "experiments identified "
                "active radical species."
            ),
            page_number=9,
            section_role=(
                PaperSectionRole.MECHANISM
            ),
        ),
        make_passage(
            passage_id="PAS-0005",
            text=(
                "The conduction band and "
                "valence band positions "
                "explain the observed "
                "radical species."
            ),
            page_number=9,
            section_role=(
                PaperSectionRole.MECHANISM
            ),
        ),
    ]

    result = (
        extract_mechanism_candidates(
            passages
        )
    )

    assert len(
        result.mechanism_claims
    ) == 1

    assert (
        result.mechanism_claims[
            0
        ].mechanism_normalized
        == MechanismLabel.Z_SCHEME
    )

    assert (
        result.mechanism_claims[
            0
        ].charge_transfer_class
        is None
    )

    characterization_types = {
        candidate.evidence_type
        for candidate
        in result.characterization_candidates
    }

    assert (
        "mott_schottky"
        in characterization_types
    )

    assert (
        "photoluminescence"
        in characterization_types
    )

    assert (
        "radical_trapping"
        in characterization_types
    )

    assert (
        "band_alignment"
        in characterization_types
    )

    mechanism_evidence_types = {
        candidate.evidence_type
        for candidate
        in result.mechanism_evidence_candidates
    }

    assert (
        "radical_trapping"
        in mechanism_evidence_types
    )

    assert (
        "band_alignment"
        in mechanism_evidence_types
    )

    assert (
        "photoluminescence"
        not in mechanism_evidence_types
    )

    assert (
        "mott_schottky"
        not in mechanism_evidence_types
    )

