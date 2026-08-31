import pytest

from pydantic import (
    ValidationError,
)

from psk_tmd.corpus.access.models import (
    AccessRecord,
    AccessStatus,
    AcquisitionRoute,
    FullTextFormat,
    TDMStatus,
)


# ---------------------------------------------------------------------------
# MINIMAL ACCESS RECORD
# ---------------------------------------------------------------------------
def test_minimal_access_record():
    record = AccessRecord(
        access_id="ACC-000001",
        candidate_id="CND-000001",
    )

    assert (
        record.access_status
        == AccessStatus.REQUIRES_REVIEW
    )

    assert (
        record.acquisition_route
        == AcquisitionRoute.NONE
    )

    assert (
        record.tdm_status
        == TDMStatus.NOT_EVALUATED
    )

    assert (
        record.full_text_available
        is False
    )


# ---------------------------------------------------------------------------
# NORMALIZE DOI
# ---------------------------------------------------------------------------
def test_normalize_doi():
    record = AccessRecord(
        access_id="ACC-000001",
        candidate_id="CND-000001",
        doi=(
            "https://doi.org/"
            "10.1016/J.CEJ.2020.125721"
        ),
    )

    assert (
        record.doi
        == "10.1016/j.cej.2020.125721"
    )


# ---------------------------------------------------------------------------
# NORMALIZE OPTIONAL TEXT
# ---------------------------------------------------------------------------
def test_normalize_optional_text():
    record = AccessRecord(
        access_id="ACC-000001",
        candidate_id="CND-000001",
        publisher="  Elsevier   B.V.  ",
        notes="   ",
    )

    assert (
        record.publisher
        == "Elsevier B.V."
    )

    assert (
        record.notes
        is None
    )


# ---------------------------------------------------------------------------
# REQUIRED ID MUST NOT BE EMPTY
# ---------------------------------------------------------------------------
def test_required_id_must_not_be_empty():
    with pytest.raises(
        ValidationError,
    ):
        AccessRecord(
            access_id="   ",
            candidate_id="CND-000001",
        )


# ---------------------------------------------------------------------------
# FULL ACCESS RECORD
# ---------------------------------------------------------------------------
def test_full_access_record():
    record = AccessRecord(
        access_id="ACC-000001",
        candidate_id="CND-000001",
        doi="10.1000/example",
        publisher="Example Publisher",
        is_open_access=True,
        oa_status="gold",
        license="CC BY 4.0",
        license_url=(
            "https://creativecommons.org/"
            "licenses/by/4.0/"
        ),
        access_status=(
            AccessStatus.AVAILABLE
        ),
        acquisition_route=(
            AcquisitionRoute.OFFICIAL_API
        ),
        source_url=(
            "https://example.org/article.xml"
        ),
        source_version="version_of_record",
        tdm_status=(
            TDMStatus.PERMITTED
        ),
        tdm_basis=(
            "Publisher API terms permit "
            "research text and data mining."
        ),
        full_text_available=True,
        full_text_format=(
            FullTextFormat.XML
        ),
        retrieval_date="2026-08-31",
        checksum="abc123",
        notes="Test access record.",
    )

    assert (
        record.full_text_available
        is True
    )

    assert (
        record.full_text_format
        == FullTextFormat.XML
    )

    assert (
        record.access_status
        == AccessStatus.AVAILABLE
    )


# ---------------------------------------------------------------------------
# FORMAT REQUIRES FULL TEXT
# ---------------------------------------------------------------------------
def test_format_requires_full_text():
    with pytest.raises(
        ValidationError,
        match=(
            "full_text_format requires "
            "full_text_available=True"
        ),
    ):
        AccessRecord(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            full_text_available=False,
            full_text_format=(
                FullTextFormat.PDF
            ),
        )


# ---------------------------------------------------------------------------
# ENUM VALUES
# ---------------------------------------------------------------------------
def test_enum_values():
    assert (
        AccessStatus.AVAILABLE.value
        == "available"
    )

    assert (
        AcquisitionRoute.OA_REPOSITORY.value
        == "oa_repository"
    )

    assert (
        TDMStatus.UNCLEAR.value
        == "unclear"
    )

    assert (
        FullTextFormat.PDF.value
        == "pdf"
    )

