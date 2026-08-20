from psk_tmd.common.constants import (
    MechanismLabel,
)
from psk_tmd.corpus.consistency import (
    CarrierPathwayType,
    MechanismConsistencyStatus,
    check_mechanism_consistency,
    classify_carrier_pathway,
    normalize_mechanism_text,
)


# ---------------------------------------------------------------------------
# NORMALIZE SOFT HYPHEN
# ---------------------------------------------------------------------------
def test_normalize_soft_hyphen():
    text = (
        "con\u00adduction band"
    )

    normalized = (
        normalize_mechanism_text(
            text
        )
    )

    assert (
        normalized
        == "conduction band"
    )


# ---------------------------------------------------------------------------
# NORMALIZE LINE-BREAK HYPHEN
# ---------------------------------------------------------------------------
def test_normalize_line_break_hyphen():
    text = (
        "photo-\n"
        "generated carriers"
    )

    normalized = (
        normalize_mechanism_text(
            text
        )
    )

    assert (
        normalized
        == "photogenerated carriers"
    )


# ---------------------------------------------------------------------------
# TYPE-II-LIKE PATHWAY
# ---------------------------------------------------------------------------
def test_classify_type_ii_like_pathway():
    text = (
        "Electrons in the conduction band "
        "of material A transfer to the "
        "conduction band of material B, "
        "while holes move from the valence "
        "band of material B to the valence "
        "band of material A."
    )

    pathway, matches = (
        classify_carrier_pathway(
            text
        )
    )

    assert (
        pathway
        == CarrierPathwayType.TYPE_II_LIKE
    )

    assert matches


# ---------------------------------------------------------------------------
# MEDIATED RECOMBINATION PATHWAY
# ---------------------------------------------------------------------------
def test_classify_mediated_recombination_pathway():
    text = (
        "Electrons in the conduction band "
        "of material A recombine with holes "
        "in the valence band of material B "
        "at the interface."
    )

    pathway, matches = (
        classify_carrier_pathway(
            text
        )
    )

    assert (
        pathway
        == (
            CarrierPathwayType
            .MEDIATED_RECOMBINATION_LIKE
        )
    )

    assert matches


# ---------------------------------------------------------------------------
# Z-SCHEME WITH TYPE-II-LIKE TEXT
# ---------------------------------------------------------------------------
def test_z_scheme_type_ii_like_is_potentially_inconsistent():
    result = (
        check_mechanism_consistency(
            reported_mechanism=(
                MechanismLabel.Z_SCHEME
            ),
            source_text=(
                "Electrons in the conduction "
                "band of WS2 transfer to the "
                "conduction band of CaTiO3, "
                "while holes move from the "
                "valence band of CaTiO3 to "
                "the valence band of WS2."
            ),
        )
    )

    assert (
        result.pathway_type
        == CarrierPathwayType.TYPE_II_LIKE
    )

    assert (
        result.consistency_status
        == (
            MechanismConsistencyStatus
            .POTENTIALLY_INCONSISTENT
        )
    )


# ---------------------------------------------------------------------------
# Z-SCHEME WITH RECOMBINATION TEXT
# ---------------------------------------------------------------------------
def test_z_scheme_recombination_path_is_consistent():
    result = (
        check_mechanism_consistency(
            reported_mechanism=(
                MechanismLabel.Z_SCHEME
            ),
            source_text=(
                "Electrons in the conduction "
                "band of material A recombine "
                "with holes in the valence "
                "band of material B at the "
                "interface."
            ),
        )
    )

    assert (
        result.pathway_type
        == (
            CarrierPathwayType
            .MEDIATED_RECOMBINATION_LIKE
        )
    )

    assert (
        result.consistency_status
        == (
            MechanismConsistencyStatus
            .CONSISTENT
        )
    )


# ---------------------------------------------------------------------------
# TYPE-II WITH TYPE-II-LIKE TEXT
# ---------------------------------------------------------------------------
def test_type_ii_path_is_consistent():
    result = (
        check_mechanism_consistency(
            reported_mechanism=(
                MechanismLabel.TYPE_II
            ),
            source_text=(
                "Electrons in the conduction "
                "band of material A transfer "
                "to the conduction band of "
                "material B, while holes move "
                "from the valence band of "
                "material B to the valence "
                "band of material A."
            ),
        )
    )

    assert (
        result.consistency_status
        == (
            MechanismConsistencyStatus
            .CONSISTENT
        )
    )


# ---------------------------------------------------------------------------
# INSUFFICIENT PATHWAY INFORMATION
# ---------------------------------------------------------------------------
def test_insufficient_pathway_information():
    result = (
        check_mechanism_consistency(
            reported_mechanism=(
                MechanismLabel.Z_SCHEME
            ),
            source_text=(
                "The heterostructure showed "
                "improved photocatalytic "
                "performance."
            ),
        )
    )

    assert (
        result.pathway_type
        == CarrierPathwayType.UNRESOLVED
    )

    assert (
        result.consistency_status
        == (
            MechanismConsistencyStatus
            .INSUFFICIENT_INFORMATION
        )
    )


# ---------------------------------------------------------------------------
# SOFT HYPHEN DOES NOT BREAK TYPE-II PATHWAY
# ---------------------------------------------------------------------------
def test_soft_hyphen_does_not_break_type_ii_pathway():
    text = (
        "Electrons in the conduction band "
        "of WS2 transfer to the con\u00adduction "
        "band of CaTiO3, while holes move "
        "from the valence band of CaTiO3 "
        "to the valence band of WS2."
    )

    pathway, matches = (
        classify_carrier_pathway(
            text
        )
    )

    assert (
        pathway
        == CarrierPathwayType.TYPE_II_LIKE
    )

    assert matches


# ---------------------------------------------------------------------------
# SELECTIVE-CARRIER EQUATION
# ---------------------------------------------------------------------------
def test_selective_carrier_equation_is_mediated_like():
    text = (
        "WS2(e− + h+) + CaTiO3(e− + h+) "
        "→ WS2(e−) + CaTiO3(h+)"
    )

    pathway, matches = (
        classify_carrier_pathway(
            text
        )
    )

    assert (
        pathway
        == (
            CarrierPathwayType
            .MEDIATED_RECOMBINATION_LIKE
        )
    )

    assert matches


# ---------------------------------------------------------------------------
# CONFLICTING PATHWAY DESCRIPTIONS
# ---------------------------------------------------------------------------
def test_conflicting_pathway_descriptions():
    text = (
        "Electrons in the conduction band "
        "of WS2 transfer to the conduction "
        "band of CaTiO3, while holes move "
        "from the valence band of CaTiO3 "
        "to the valence band of WS2. "
        "WS2(e− + h+) + CaTiO3(e− + h+) "
        "→ WS2(e−) + CaTiO3(h+)."
    )

    result = (
        check_mechanism_consistency(
            reported_mechanism=(
                MechanismLabel.Z_SCHEME
            ),
            source_text=text,
        )
    )

    assert (
        result.pathway_type
        == CarrierPathwayType.CONFLICTING
    )

    assert (
        result.consistency_status
        == (
            MechanismConsistencyStatus
            .INTERNALLY_CONFLICTING
        )
    )


# ---------------------------------------------------------------------------
# RASHKI-STYLE CONFLICTING PATHWAY
# ---------------------------------------------------------------------------
def test_rashki_style_pathway_is_conflicting():
    text = (
        "The valence band and conduction band "
        "corresponding to WS2 are at a higher "
        "position than those corresponding to "
        "CaTiO3. So, the electrons that are "
        "reaching the conduction band of WS2 "
        "can easily transfer to the conduction "
        "band of CaTiO3 and the holes can "
        "easily move from CaTiO3 to the WS2 "
        "nanosheets. "
        "WS2(e− + h+) + CaTiO3(e− + h+) "
        "→ WS2(e−) + CaTiO3(h+)."
    )

    result = (
        check_mechanism_consistency(
            reported_mechanism=(
                MechanismLabel.Z_SCHEME
            ),
            source_text=text,
        )
    )

    assert (
        result.pathway_type
        == CarrierPathwayType.CONFLICTING
    )

    assert (
        result.consistency_status
        == (
            MechanismConsistencyStatus
            .INTERNALLY_CONFLICTING
        )
    )


# ---------------------------------------------------------------------------
# JIANG-STYLE MEDIATED RECOMBINATION
# ---------------------------------------------------------------------------
def test_jiang_style_mediated_recombination():
    text = (
        "Simultaneously, the rapid recombination "
        "of electrons on the CB of CaTiO3 and "
        "the holes on the VB of MoS2 takes "
        "place at their interface."
    )

    result = (
        check_mechanism_consistency(
            reported_mechanism=(
                MechanismLabel.Z_SCHEME
            ),
            source_text=text,
        )
    )

    assert (
        result.pathway_type
        == (
            CarrierPathwayType
            .MEDIATED_RECOMBINATION_LIKE
        )
    )

    assert (
        result.consistency_status
        == (
            MechanismConsistencyStatus
            .CONSISTENT
        )
    )


