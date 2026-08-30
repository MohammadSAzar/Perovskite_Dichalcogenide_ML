import pytest

from pydantic import (
    ValidationError,
)

from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
    normalize_doi,
    normalize_optional_text,
)


# ---------------------------------------------------------------------------
# OPTIONAL TEXT NORMALIZATION
# ---------------------------------------------------------------------------
def test_normalize_optional_text():
    assert (
        normalize_optional_text(
            "  Chemical   Engineering "
            " Journal  "
        )
        == "Chemical Engineering Journal"
    )

    assert (
        normalize_optional_text(
            "   "
        )
        is None
    )

    assert (
        normalize_optional_text(
            None
        )
        is None
    )


# ---------------------------------------------------------------------------
# DOI NORMALIZATION
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    (
        "raw_doi",
        "expected",
    ),
    [
        (
            "10.1016/j.cej.2020.125721",
            "10.1016/j.cej.2020.125721",
        ),
        (
            "https://doi.org/"
            "10.1016/j.cej.2020.125721",
            "10.1016/j.cej.2020.125721",
        ),
        (
            "http://dx.doi.org/"
            "10.1016/J.CEJ.2020.125721",
            "10.1016/j.cej.2020.125721",
        ),
        (
            "DOI: "
            "10.1016/J.CEJ.2020.125721",
            "10.1016/j.cej.2020.125721",
        ),
    ],
)
def test_normalize_doi(
    raw_doi,
    expected,
):
    assert (
        normalize_doi(
            raw_doi
        )
        == expected
    )


# ---------------------------------------------------------------------------
# MINIMAL DISCOVERY RECORD
# ---------------------------------------------------------------------------
def test_minimal_discovery_record():
    record = DiscoveryRecord(
        discovery_id="DSC-0001",
        title=(
            "Construction of a Z-scheme "
            "MoS2/CaTiO3 heterostructure"
        ),
        source="crossref",
    )

    assert (
        record.discovery_id
        == "DSC-0001"
    )

    assert (
        record.source
        == "crossref"
    )

    assert record.doi is None

    assert record.authors == []

    assert (
        record.is_open_access
        is None
    )


# ---------------------------------------------------------------------------
# COMPLETE DISCOVERY RECORD
# ---------------------------------------------------------------------------
def test_complete_discovery_record():
    record = DiscoveryRecord(
        discovery_id="DSC-0002",
        doi=(
            "https://doi.org/"
            "10.1016/j.cej.2020.125721"
        ),
        title=(
            "  Construction   of a "
            "Z-scheme MoS2/CaTiO3 "
            "heterostructure  "
        ),
        authors=[
            " Enhui   Jiang ",
            " Ning Song ",
            "",
        ],
        year=2020,
        journal=(
            " Chemical Engineering "
            "Journal "
        ),
        publisher=" Elsevier B.V. ",
        abstract=(
            "  A photocatalytic "
            "heterostructure was studied. "
        ),
        source=" crossref ",
        source_id=(
            "10.1016/j.cej.2020.125721"
        ),
        is_open_access=False,
        landing_page_url=(
            " https://doi.org/"
            "10.1016/j.cej.2020.125721 "
        ),
    )

    assert (
        record.doi
        == "10.1016/j.cej.2020.125721"
    )

    assert (
        record.title
        == (
            "Construction of a Z-scheme "
            "MoS2/CaTiO3 heterostructure"
        )
    )

    assert record.authors == [
        "Enhui Jiang",
        "Ning Song",
    ]

    assert (
        record.journal
        == "Chemical Engineering Journal"
    )

    assert (
        record.publisher
        == "Elsevier B.V."
    )

    assert (
        record.source
        == "crossref"
    )

    assert (
        record.is_open_access
        is False
    )


# ---------------------------------------------------------------------------
# EMPTY REQUIRED TEXT FAILS
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "field_name",
    [
        "discovery_id",
        "title",
        "source",
    ],
)
def test_empty_required_text_fails(
    field_name,
):
    payload = {"discovery_id": "DSC-0001", "title": "Test paper", "source": "crossref", field_name: "   "}

    with pytest.raises(
        ValidationError,
        match="must not be empty",
    ):
        DiscoveryRecord(
            **payload
        )


# ---------------------------------------------------------------------------
# INVALID YEAR FAILS
# ---------------------------------------------------------------------------
def test_invalid_year_fails():
    with pytest.raises(
        ValidationError,
    ):
        DiscoveryRecord(
            discovery_id="DSC-0003",
            title="Test paper",
            year=999,
            source="openalex",
        )


# ---------------------------------------------------------------------------
# UNKNOWN OA STATUS IS PRESERVED
# ---------------------------------------------------------------------------
def test_unknown_oa_status_is_preserved():
    record = DiscoveryRecord(
        discovery_id="DSC-0004",
        title="Test paper",
        source="openalex",
        is_open_access=None,
    )

    assert (
        record.is_open_access
        is None
    )

