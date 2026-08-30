import pytest

from psk_tmd.corpus.discovery.deduplication import (
    deduplicate_discovery_records,
    get_discovery_group_key,
    merge_discovery_group,
    normalize_title_key,
    select_open_access_status,
    select_year,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)


# ---------------------------------------------------------------------------
# MAKE DISCOVERY RECORD
# ---------------------------------------------------------------------------
def make_record(
    discovery_id: str,
    *,
    doi: str | None,
    title: str,
    source: str,
    year: int | None = None,
    abstract: str | None = None,
    is_open_access: bool | None = None,
) -> DiscoveryRecord:
    return DiscoveryRecord(
        discovery_id=discovery_id,
        doi=doi,
        title=title,
        authors=[],
        year=year,
        journal=None,
        publisher=None,
        abstract=abstract,
        source=source,
        source_id=None,
        is_open_access=(
            is_open_access
        ),
        landing_page_url=None,
    )


# ---------------------------------------------------------------------------
# NORMALIZE TITLE KEY
# ---------------------------------------------------------------------------
def test_normalize_title_key():
    result = (
        normalize_title_key(
            "MoS2 / CaTiO3: "
            "Z-scheme Photocatalysis!"
        )
    )

    assert result == (
        "mos2catio3"
        "zschemephotocatalysis"
    )


# ---------------------------------------------------------------------------
# DOI GROUP KEY
# ---------------------------------------------------------------------------
def test_group_key_prefers_doi():
    record = make_record(
        "DSC-000001",
        doi=(
            "10.1016/test"
        ),
        title="Test article",
        source="crossref",
    )

    assert (
        get_discovery_group_key(
            record
        )
        == "doi:10.1016/test"
    )


# ---------------------------------------------------------------------------
# TITLE FALLBACK GROUP KEY
# ---------------------------------------------------------------------------
def test_group_key_uses_title_without_doi():
    record = make_record(
        "DSC-000001",
        doi=None,
        title=(
            "Test Article"
        ),
        source="openalex",
    )

    assert (
        get_discovery_group_key(
            record
        )
        == "title:testarticle"
    )


# ---------------------------------------------------------------------------
# SELECT YEAR
# ---------------------------------------------------------------------------
def test_select_year_uses_earliest():
    records = [
        make_record(
            "DSC-000001",
            doi="10.1/test",
            title="Test",
            source="crossref",
            year=2024,
        ),
        make_record(
            "DSC-000002",
            doi="10.1/test",
            title="Test",
            source="openalex",
            year=2023,
        ),
    ]

    assert (
        select_year(
            records
        )
        == 2023
    )


# ---------------------------------------------------------------------------
# SELECT OPEN ACCESS STATUS
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    (
        "values",
        "expected",
    ),
    [
        (
            [
                None,
                None,
            ],
            None,
        ),
        (
            [
                None,
                False,
            ],
            False,
        ),
        (
            [
                False,
                True,
            ],
            True,
        ),
    ],
)
def test_select_open_access_status(
    values,
    expected,
):
    records = [
        make_record(
            f"DSC-{index:06d}",
            doi=(
                "10.1/test"
            ),
            title="Test",
            source=(
                f"source-{index}"
            ),
            is_open_access=value,
        )
        for (
            index,
            value,
        ) in enumerate(
            values,
            start=1,
        )
    ]

    assert (
        select_open_access_status(
            records
        )
        is expected
    )


# ---------------------------------------------------------------------------
# MERGE SAME DOI
# ---------------------------------------------------------------------------
def test_merge_same_doi():
    crossref = make_record(
        "DSC-000001",
        doi=(
            "10.1016/"
            "j.chemosphere.2023.140575"
        ),
        title=(
            "Boosting the performance "
            "of LaCoO3/MoS2"
        ),
        source="crossref",
        year=2024,
        is_open_access=None,
    )

    openalex = make_record(
        "DSC-000002",
        doi=(
            "10.1016/"
            "j.chemosphere.2023.140575"
        ),
        title=(
            "Boosting the performance "
            "of LaCoO3/MoS2"
        ),
        source="openalex",
        year=2023,
        is_open_access=False,
    )

    merged = (
        merge_discovery_group(
            [
                crossref,
                openalex,
            ],
            discovery_id=(
                "DSC-000010"
            ),
        )
    )

    assert (
        merged.discovery_id
        == "DSC-000010"
    )

    assert (
        merged.doi
        == (
            "10.1016/"
            "j.chemosphere.2023.140575"
        )
    )

    assert (
        merged.year
        == 2023
    )

    assert (
        merged.source
        == "crossref+openalex"
    )

    assert (
        merged.is_open_access
        is False
    )


# ---------------------------------------------------------------------------
# CONFLICTING DOI FAILS
# ---------------------------------------------------------------------------
def test_conflicting_doi_fails():
    records = [
        make_record(
            "DSC-000001",
            doi="10.1/one",
            title="Test",
            source="crossref",
        ),
        make_record(
            "DSC-000002",
            doi="10.1/two",
            title="Test",
            source="openalex",
        ),
    ]

    with pytest.raises(
        ValueError,
        match="conflicting DOIs",
    ):
        merge_discovery_group(
            records,
            discovery_id=(
                "DSC-000003"
            ),
        )


# ---------------------------------------------------------------------------
# DEDUPLICATE DISCOVERY RECORDS
# ---------------------------------------------------------------------------
def test_deduplicate_discovery_records():
    records = [
        make_record(
            "DSC-000001",
            doi="10.1/shared",
            title="Shared paper",
            source="crossref",
        ),
        make_record(
            "DSC-000002",
            doi="10.1/shared",
            title="Shared paper",
            source="openalex",
        ),
        make_record(
            "DSC-000003",
            doi="10.1/unique",
            title="Unique paper",
            source="crossref",
        ),
    ]

    merged = (
        deduplicate_discovery_records(
            records
        )
    )

    assert len(
        merged
    ) == 2

    dois = {
        record.doi
        for record in merged
    }

    assert dois == {
        "10.1/shared",
        "10.1/unique",
    }

