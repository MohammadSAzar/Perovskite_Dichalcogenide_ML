import pytest

from psk_tmd.corpus.discovery.crossref import (
    build_crossref_discovery_record,
    build_crossref_discovery_records,
    build_crossref_url,
    clean_crossref_abstract,
    format_crossref_author,
    get_crossref_authors,
    get_crossref_year,
)


# ---------------------------------------------------------------------------
# CROSSREF SAMPLE ITEM
# ---------------------------------------------------------------------------
def make_crossref_item():
    return {
        "DOI": (
            "10.1016/"
            "j.cej.2020.125721"
        ),
        "title": [
            "Construction of a Z-scheme "
            "MoS2/CaTiO3 heterostructure"
        ],
        "author": [
            {
                "given": "Enhui",
                "family": "Jiang",
            },
            {
                "given": "Ning",
                "family": "Song",
            },
        ],
        "published-print": {
            "date-parts": [
                [
                    2020,
                    11,
                ]
            ]
        },
        "container-title": [
            "Chemical Engineering Journal"
        ],
        "publisher": (
            "Elsevier BV"
        ),
        "abstract": (
            "<jats:p>"
            "A photocatalytic "
            "heterostructure was studied."
            "</jats:p>"
        ),
        "URL": (
            "https://doi.org/"
            "10.1016/"
            "j.cej.2020.125721"
        ),
    }


# ---------------------------------------------------------------------------
# CLEAN CROSSREF ABSTRACT
# ---------------------------------------------------------------------------
def test_clean_crossref_abstract():
    result = (
        clean_crossref_abstract(
            "<jats:p>"
            "Photocatalytic &amp; "
            "electronic properties."
            "</jats:p>"
        )
    )

    assert result == (
        "Photocatalytic & "
        "electronic properties."
    )


# ---------------------------------------------------------------------------
# FORMAT CROSSREF AUTHOR
# ---------------------------------------------------------------------------
def test_format_crossref_author():
    result = (
        format_crossref_author(
            {
                "given": "Enhui",
                "family": "Jiang",
            }
        )
    )

    assert result == "Enhui Jiang"


# ---------------------------------------------------------------------------
# GET CROSSREF AUTHORS
# ---------------------------------------------------------------------------
def test_get_crossref_authors():
    authors = (
        get_crossref_authors(
            make_crossref_item()
        )
    )

    assert authors == [
        "Enhui Jiang",
        "Ning Song",
    ]


# ---------------------------------------------------------------------------
# GET CROSSREF YEAR
# ---------------------------------------------------------------------------
def test_get_crossref_year():
    year = (
        get_crossref_year(
            make_crossref_item()
        )
    )

    assert year == 2020


# ---------------------------------------------------------------------------
# YEAR FALLBACK
# ---------------------------------------------------------------------------
def test_crossref_year_falls_back_to_issued():
    item = {
        "issued": {
            "date-parts": [
                [
                    2023,
                ]
            ]
        }
    }

    assert (
        get_crossref_year(
            item
        )
        == 2023
    )


# ---------------------------------------------------------------------------
# BUILD CROSSREF DISCOVERY RECORD
# ---------------------------------------------------------------------------
def test_build_crossref_discovery_record():
    record = (
        build_crossref_discovery_record(
            make_crossref_item(),
            discovery_id="DSC-000001",
        )
    )

    assert (
        record.discovery_id
        == "DSC-000001"
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

    assert record.year == 2020

    assert (
        record.journal
        == "Chemical Engineering Journal"
    )

    assert (
        record.publisher
        == "Elsevier BV"
    )

    assert (
        record.source
        == "crossref"
    )

    assert (
        record.source_id
        == "10.1016/j.cej.2020.125721"
    )

    assert (
        record.is_open_access
        is None
    )


# ---------------------------------------------------------------------------
# MISSING TITLE FAILS
# ---------------------------------------------------------------------------
def test_missing_crossref_title_fails():
    item = (
        make_crossref_item()
    )

    item[
        "title"
    ] = []

    with pytest.raises(
        ValueError,
        match="missing a usable title",
    ):
        build_crossref_discovery_record(
            item,
            discovery_id="DSC-000001",
        )


# ---------------------------------------------------------------------------
# BAD ITEMS ARE SKIPPED
# ---------------------------------------------------------------------------
def test_bad_crossref_items_are_skipped():
    valid = (
        make_crossref_item()
    )

    invalid = {
        "DOI": (
            "10.0000/missing-title"
        )
    }

    records = (
        build_crossref_discovery_records(
            [
                invalid,
                valid,
            ]
        )
    )

    assert len(
        records
    ) == 1

    assert (
        records[
            0
        ].discovery_id
        == "DSC-000001"
    )


# ---------------------------------------------------------------------------
# BUILD CROSSREF URL
# ---------------------------------------------------------------------------
def test_build_crossref_url():
    url = build_crossref_url(
        (
            "perovskite MoS2 "
            "photocatalysis"
        ),
        rows=50,
        mailto=(
            "researcher@example.com"
        ),
    )

    assert (
        url.startswith(
            "https://api.crossref.org/"
            "works?"
        )
    )

    assert (
        "query.bibliographic="
        in url
    )

    assert "rows=50" in url

    assert (
        "mailto="
        "researcher%40example.com"
        in url
    )


# ---------------------------------------------------------------------------
# EMPTY CROSSREF QUERY FAILS
# ---------------------------------------------------------------------------
def test_empty_crossref_query_fails():
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        build_crossref_url(
            "   "
        )


# ---------------------------------------------------------------------------
# INVALID CROSSREF ROW COUNT FAILS
# ---------------------------------------------------------------------------
def test_invalid_crossref_row_count_fails():
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        build_crossref_url(
            "photocatalysis",
            rows=0,
        )

