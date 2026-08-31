from datetime import (
    date,
)

import pytest

from psk_tmd.corpus.access.evidence import (
    AccessEvidenceSource,
    AccessEvidenceType,
)
from psk_tmd.corpus.access.models import (
    AccessRecord,
)
from psk_tmd.corpus.access.openalex import (
    build_license_evidence,
    build_location_evidence,
    build_oa_status_evidence,
    build_openalex_access_evidence,
    build_openalex_doi_url,
    build_version_evidence,
    get_best_oa_location,
    get_location_source_name,
    get_location_url,
    get_open_access,
)


# ---------------------------------------------------------------------------
# MAKE ACCESS RECORD
# ---------------------------------------------------------------------------
def make_access_record() -> AccessRecord:
    return AccessRecord(
        access_id="ACC-000001",
        candidate_id="CND-000001",
        doi=(
            "10.1000/example"
        ),
    )


# ---------------------------------------------------------------------------
# MAKE OPENALEX WORK
# ---------------------------------------------------------------------------
def make_work() -> dict:
    return {
        "id": (
            "https://openalex.org/"
            "W123456789"
        ),
        "open_access": {
            "is_oa": True,
            "oa_status": "gold",
            "oa_url": (
                "https://example.org/article"
            ),
        },
        "best_oa_location": {
            "landing_page_url": (
                "https://example.org/article"
            ),
            "pdf_url": (
                "https://example.org/article.pdf"
            ),
            "is_oa": True,
            "version": (
                "publishedVersion"
            ),
            "license": (
                "cc-by"
            ),
            "source": {
                "display_name": (
                    "Example Journal"
                ),
            },
        },
    }


# ---------------------------------------------------------------------------
# BUILD DOI URL
# ---------------------------------------------------------------------------
def test_build_openalex_doi_url():
    url = build_openalex_doi_url(
        "10.1000/Example"
    )

    assert url == (
        "https://api.openalex.org/works/"
        "https%3A%2F%2Fdoi.org%2F"
        "10.1000%2Fexample"
    )


# ---------------------------------------------------------------------------
# BUILD DOI URL WITH API KEY
# ---------------------------------------------------------------------------
def test_build_openalex_doi_url_with_api_key():
    url = build_openalex_doi_url(
        "10.1000/example",
        api_key="test-key",
    )

    assert (
        url.endswith(
            "?api_key=test-key"
        )
    )


# ---------------------------------------------------------------------------
# GET OPEN ACCESS
# ---------------------------------------------------------------------------
def test_get_open_access():
    work = make_work()

    result = get_open_access(
        work
    )

    assert (
        result[
            "oa_status"
        ]
        == "gold"
    )


# ---------------------------------------------------------------------------
# GET MISSING OPEN ACCESS
# ---------------------------------------------------------------------------
def test_get_missing_open_access():
    assert (
        get_open_access(
            {}
        )
        == {}
    )


# ---------------------------------------------------------------------------
# GET BEST OA LOCATION
# ---------------------------------------------------------------------------
def test_get_best_oa_location():
    result = (
        get_best_oa_location(
            make_work()
        )
    )

    assert (
        result[
            "version"
        ]
        == "publishedVersion"
    )


# ---------------------------------------------------------------------------
# GET LOCATION SOURCE NAME
# ---------------------------------------------------------------------------
def test_get_location_source_name():
    result = (
        get_location_source_name(
            make_work()[
                "best_oa_location"
            ]
        )
    )

    assert (
        result
        == "Example Journal"
    )


# ---------------------------------------------------------------------------
# PDF URL IS PREFERRED
# ---------------------------------------------------------------------------
def test_pdf_url_is_preferred():
    result = (
        get_location_url(
            make_work()[
                "best_oa_location"
            ]
        )
    )

    assert (
        result
        == (
            "https://example.org/"
            "article.pdf"
        )
    )


# ---------------------------------------------------------------------------
# LANDING PAGE FALLBACK
# ---------------------------------------------------------------------------
def test_landing_page_fallback():
    location = (
        make_work()[
            "best_oa_location"
        ].copy()
    )

    location[
        "pdf_url"
    ] = None

    result = (
        get_location_url(
            location
        )
    )

    assert (
        result
        == (
            "https://example.org/article"
        )
    )


# ---------------------------------------------------------------------------
# BUILD OA STATUS EVIDENCE
# ---------------------------------------------------------------------------
def test_build_oa_status_evidence():
    evidence = (
        build_oa_status_evidence(
            make_access_record(),
            make_work(),
            evidence_id=(
                "AEV-000001"
            ),
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
        )
    )

    assert (
        evidence.evidence_type
        == AccessEvidenceType.OA_STATUS
    )

    assert (
        evidence.source
        == AccessEvidenceSource.OPENALEX
    )

    assert (
        evidence.value
        == "gold"
    )


# ---------------------------------------------------------------------------
# CLOSED OA STATUS EVIDENCE
# ---------------------------------------------------------------------------
def test_closed_oa_status_evidence():
    work = make_work()

    work[
        "open_access"
    ] = {
        "is_oa": False,
        "oa_status": "closed",
    }

    evidence = (
        build_oa_status_evidence(
            make_access_record(),
            work,
            evidence_id=(
                "AEV-000001"
            ),
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
        )
    )

    assert (
        evidence.value
        == "closed"
    )


# ---------------------------------------------------------------------------
# BUILD LOCATION EVIDENCE
# ---------------------------------------------------------------------------
def test_build_location_evidence():
    evidence = (
        build_location_evidence(
            make_access_record(),
            make_work(),
            evidence_id=(
                "AEV-000002"
            ),
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
        )
    )

    assert evidence is not None

    assert (
        evidence.evidence_type
        == AccessEvidenceType.FULL_TEXT_LOCATION
    )

    assert (
        evidence.source_url
        == (
            "https://example.org/"
            "article.pdf"
        )
    )


# ---------------------------------------------------------------------------
# LOCATION EVIDENCE MAY BE ABSENT
# ---------------------------------------------------------------------------
def test_location_evidence_may_be_absent():
    work = make_work()

    work[
        "best_oa_location"
    ] = None

    evidence = (
        build_location_evidence(
            make_access_record(),
            work,
            evidence_id=(
                "AEV-000002"
            ),
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
        )
    )

    assert evidence is None


# ---------------------------------------------------------------------------
# BUILD LICENSE EVIDENCE
# ---------------------------------------------------------------------------
def test_build_license_evidence():
    evidence = (
        build_license_evidence(
            make_access_record(),
            make_work(),
            evidence_id=(
                "AEV-000003"
            ),
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
        )
    )

    assert evidence is not None

    assert (
        evidence.evidence_type
        == AccessEvidenceType.LICENSE
    )

    assert (
        evidence.value
        == "cc-by"
    )


# ---------------------------------------------------------------------------
# LICENSE EVIDENCE MAY BE ABSENT
# ---------------------------------------------------------------------------
def test_license_evidence_may_be_absent():
    work = make_work()

    work[
        "best_oa_location"
    ][
        "license"
    ] = None

    evidence = (
        build_license_evidence(
            make_access_record(),
            work,
            evidence_id=(
                "AEV-000003"
            ),
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
        )
    )

    assert evidence is None


# ---------------------------------------------------------------------------
# BUILD VERSION EVIDENCE
# ---------------------------------------------------------------------------
def test_build_version_evidence():
    evidence = (
        build_version_evidence(
            make_access_record(),
            make_work(),
            evidence_id=(
                "AEV-000004"
            ),
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
        )
    )

    assert evidence is not None

    assert (
        evidence.evidence_type
        == AccessEvidenceType.VERSION
    )

    assert (
        evidence.value
        == "publishedVersion"
    )


# ---------------------------------------------------------------------------
# BUILD COMPLETE EVIDENCE SET
# ---------------------------------------------------------------------------
def test_build_complete_evidence_set():
    evidence = (
        build_openalex_access_evidence(
            make_access_record(),
            make_work(),
            start_index=10,
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
        )
    )

    assert len(
        evidence
    ) == 4

    assert [
        item.evidence_id
        for item in evidence
    ] == [
        "AEV-000010",
        "AEV-000011",
        "AEV-000012",
        "AEV-000013",
    ]


# ---------------------------------------------------------------------------
# ONLY OA EVIDENCE WHEN LOCATION IS ABSENT
# ---------------------------------------------------------------------------
def test_only_oa_evidence_when_location_absent():
    work = make_work()

    work[
        "best_oa_location"
    ] = None

    evidence = (
        build_openalex_access_evidence(
            make_access_record(),
            work,
            start_index=1,
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
        )
    )

    assert len(
        evidence
    ) == 1

    assert (
        evidence[
            0
        ].evidence_type
        == AccessEvidenceType.OA_STATUS
    )


# ---------------------------------------------------------------------------
# INVALID START INDEX
# ---------------------------------------------------------------------------
def test_invalid_start_index():
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        build_openalex_access_evidence(
            make_access_record(),
            make_work(),
            start_index=0,
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
        )


