from psk_tmd.corpus.discovery.association import (
    detect_title_association,
    resolve_association_status,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)
from psk_tmd.corpus.discovery.screening import (
    DiscoveryScreeningStatus,
    screen_discovery_record,
)


# ---------------------------------------------------------------------------
# MAKE RECORD
# ---------------------------------------------------------------------------
def make_record(
    *,
    title: str,
    abstract: str | None = None,
) -> DiscoveryRecord:
    return DiscoveryRecord(
        discovery_id="DSC-000001",
        title=title,
        abstract=abstract,
        source="test",
    )


# ---------------------------------------------------------------------------
# TARGET PAIR IN TITLE
# ---------------------------------------------------------------------------
def test_target_pair_in_title():
    record = make_record(
        title=(
            "Construction of Z-scheme "
            "MoS2/CaTiO3 heterostructure "
            "for photocatalysis"
        ),
    )

    result = (
        detect_title_association(
            record
        )
    )

    assert (
        result.has_title_pair_signal
        is True
    )

    assert (
        result.matched_title_known_perovskite_formulas
        == (
            "CaTiO3",
        )
    )

    assert (
        result.matched_title_tmd_terms
        == (
            "mos2",
        )
    )


# ---------------------------------------------------------------------------
# MATERIALS ONLY IN ABSTRACT
# ---------------------------------------------------------------------------
def test_materials_only_in_abstract():
    record = make_record(
        title=(
            "Photocatalytic reduction "
            "on heterojunction catalysts"
        ),
        abstract=(
            "CaTiO3 and MoS2 were "
            "discussed among many materials."
        ),
    )

    result = (
        detect_title_association(
            record
        )
    )

    assert (
        result.has_title_pair_signal
        is False
    )


# ---------------------------------------------------------------------------
# ONLY TMD IN TITLE
# ---------------------------------------------------------------------------
def test_only_tmd_in_title():
    record = make_record(
        title=(
            "Chemical vapour deposition "
            "of MoS2 and WS2 monolayers"
        ),
        abstract=(
            "SrTiO3 substrates were used."
        ),
    )

    result = (
        detect_title_association(
            record
        )
    )

    assert (
        result.has_title_tmd_signal
        is True
    )

    assert (
        result.has_title_known_perovskite_formula
        is False
    )

    assert (
        result.has_title_pair_signal
        is False
    )


# ---------------------------------------------------------------------------
# PASS WITH TITLE PAIR REMAINS PASS
# ---------------------------------------------------------------------------
def test_pass_with_title_pair_remains_pass():
    record = make_record(
        title=(
            "CaTiO3/MoS2 composite "
            "for photocatalysis"
        ),
    )

    screening = (
        screen_discovery_record(
            record
        )
    )

    association = (
        detect_title_association(
            record
        )
    )

    status, _ = (
        resolve_association_status(
            screening,
            association,
        )
    )

    assert (
        status
        == DiscoveryScreeningStatus.PASS
    )


# ---------------------------------------------------------------------------
# PASS WITHOUT TITLE PAIR BECOMES REVIEW
# ---------------------------------------------------------------------------
def test_pass_without_title_pair_becomes_review():
    record = make_record(
        title=(
            "Advanced photocatalytic "
            "heterojunction materials"
        ),
        abstract=(
            "CaTiO3 and MoS2 were "
            "investigated for photocatalysis."
        ),
    )

    screening = (
        screen_discovery_record(
            record
        )
    )

    assert (
        screening.status
        == DiscoveryScreeningStatus.PASS
    )

    association = (
        detect_title_association(
            record
        )
    )

    status, _ = (
        resolve_association_status(
            screening,
            association,
        )
    )

    assert (
        status
        == DiscoveryScreeningStatus.REVIEW
    )


# ---------------------------------------------------------------------------
# REVIEW REMAINS REVIEW
# ---------------------------------------------------------------------------
def test_review_remains_review():
    record = make_record(
        title=(
            "Perovskite/MoS2 "
            "photocatalyst"
        ),
    )

    screening = (
        screen_discovery_record(
            record
        )
    )

    assert (
        screening.status
        == DiscoveryScreeningStatus.REVIEW
    )

    association = (
        detect_title_association(
            record
        )
    )

    status, _ = (
        resolve_association_status(
            screening,
            association,
        )
    )

    assert (
        status
        == DiscoveryScreeningStatus.REVIEW
    )


# ---------------------------------------------------------------------------
# REJECT REMAINS REJECT
# ---------------------------------------------------------------------------
def test_reject_remains_reject():
    record = make_record(
        title=(
            "MoS2/g-C3N4 "
            "photocatalyst"
        ),
    )

    screening = (
        screen_discovery_record(
            record
        )
    )

    association = (
        detect_title_association(
            record
        )
    )

    status, _ = (
        resolve_association_status(
            screening,
            association,
        )
    )

    assert (
        status
        == DiscoveryScreeningStatus.REJECT
    )


