import pytest

from psk_tmd.corpus.discovery.openalex import (
    build_openalex_discovery_record,
    build_openalex_discovery_records,
    build_openalex_url,
    get_openalex_authors,
    get_openalex_journal,
    get_openalex_oa_status,
    reconstruct_openalex_abstract,
)


# ---------------------------------------------------------------------------
# OPENALEX SAMPLE ITEM
# ---------------------------------------------------------------------------
def make_openalex_item():
    return {
        "id": (
            "https://openalex.org/"
            "W123456789"
        ),
        "doi": (
            "https://doi.org/"
            "10.1016/j.cej.2020.125721"
        ),
        "title": (
            "Construction of a Z-scheme "
            "MoS2/CaTiO3 heterostructure"
        ),
        "publication_year": 2020,
        "authorships": [
            {
                "author": {
                    "display_name": (
                        "Enhui Jiang"
                    ),
                }
            },
            {
                "author": {
                    "display_name": (
                        "Ning Song"
                    ),
                }
            },
        ],
        "primary_location": {
            "landing_page_url": (
                "https://doi.org/"
                "10.1016/j.cej.2020.125721"
            ),
            "source": {
                "display_name": (
                    "Chemical Engineering "
                    "Journal"
                ),
                "host_organization_name": (
                    "Elsevier"
                ),
            },
        },
        "open_access": {
            "is_oa": False,
        },
        "abstract_inverted_index": {
            "A": [
                0,
            ],
            "photocatalytic": [
                1,
            ],
            "heterostructure": [
                2,
            ],
            "was": [
                3,
            ],
            "studied.": [
                4,
            ],
        },
    }


# ---------------------------------------------------------------------------
# RECONSTRUCT OPENALEX ABSTRACT
# ---------------------------------------------------------------------------
def test_reconstruct_openalex_abstract():
    result = (
        reconstruct_openalex_abstract(
            {
                "Photocatalytic": [
                    0,
                ],
                "materials": [
                    1,
                ],
                "were": [
                    2,
                ],
                "studied.": [
                    3,
                ],
            }
        )
    )

    assert result == (
        "Photocatalytic materials "
        "were studied."
    )


# ---------------------------------------------------------------------------
# GET OPENALEX AUTHORS
# ---------------------------------------------------------------------------
def test_get_openalex_authors():
    authors = (
        get_openalex_authors(
            make_openalex_item()
        )
    )

    assert authors == [
        "Enhui Jiang",
        "Ning Song",
    ]


# ---------------------------------------------------------------------------
# GET OPENALEX JOURNAL
# ---------------------------------------------------------------------------
def test_get_openalex_journal():
    journal = (
        get_openalex_journal(
            make_openalex_item()
        )
    )

    assert (
        journal
        == "Chemical Engineering Journal"
    )


# ---------------------------------------------------------------------------
# GET OPENALEX OA STATUS
# ---------------------------------------------------------------------------
def test_get_openalex_oa_status():
    assert (
        get_openalex_oa_status(
            make_openalex_item()
        )
        is False
    )


# ---------------------------------------------------------------------------
# BUILD OPENALEX DISCOVERY RECORD
# ---------------------------------------------------------------------------
def test_build_openalex_discovery_record():
    record = (
        build_openalex_discovery_record(
            make_openalex_item(),
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

    assert record.year == 2020

    assert (
        record.journal
        == "Chemical Engineering Journal"
    )

    assert (
        record.publisher
        == "Elsevier"
    )

    assert (
        record.abstract
        == (
            "A photocatalytic "
            "heterostructure was studied."
        )
    )

    assert (
        record.source
        == "openalex"
    )

    assert (
        record.source_id
        == (
            "https://openalex.org/"
            "W123456789"
        )
    )

    assert (
        record.is_open_access
        is False
    )


# ---------------------------------------------------------------------------
# MISSING TITLE FAILS
# ---------------------------------------------------------------------------
def test_missing_openalex_title_fails():
    item = (
        make_openalex_item()
    )

    item[
        "title"
    ] = None

    with pytest.raises(
        ValueError,
        match="missing a usable title",
    ):
        build_openalex_discovery_record(
            item,
            discovery_id="DSC-000001",
        )


# ---------------------------------------------------------------------------
# BAD ITEMS ARE SKIPPED
# ---------------------------------------------------------------------------
def test_bad_openalex_items_are_skipped():
    valid = (
        make_openalex_item()
    )

    invalid = {
        "id": (
            "https://openalex.org/"
            "W999"
        )
    }

    records = (
        build_openalex_discovery_records(
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
# BUILD OPENALEX URL
# ---------------------------------------------------------------------------
def test_build_openalex_url():
    url = build_openalex_url(
        (
            "perovskite MoS2 "
            "photocatalysis"
        ),
        per_page=50,
        api_key="test-key",
    )

    assert (
        url.startswith(
            "https://api.openalex.org/"
            "works?"
        )
    )

    assert (
        "search="
        in url
    )

    assert (
        "filter=type%3Aarticle"
        in url
    )

    assert (
        "per-page=50"
        in url
    )

    assert (
        "api_key=test-key"
        in url
    )


# ---------------------------------------------------------------------------
# EMPTY OPENALEX QUERY FAILS
# ---------------------------------------------------------------------------
def test_empty_openalex_query_fails():
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        build_openalex_url(
            "   "
        )


# ---------------------------------------------------------------------------
# INVALID OPENALEX PER PAGE FAILS
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "per_page",
    [
        0,
        101,
    ],
)
def test_invalid_openalex_per_page_fails(
    per_page,
):
    with pytest.raises(
        ValueError,
        match="between 1 and 100",
    ):
        build_openalex_url(
            "photocatalysis",
            per_page=per_page,
        )


