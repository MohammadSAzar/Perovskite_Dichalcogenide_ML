from psk_tmd.corpus.access.location import (
    AccessLocationType,
    classify_access_location,
    is_publisher_hostname,
    normalize_hostname,
)


# ---------------------------------------------------------------------------
# NORMALIZE HOSTNAME
# ---------------------------------------------------------------------------
def test_normalize_hostname():
    assert (
        normalize_hostname(
            "  WWW.MDPI.COM "
        )
        == "www.mdpi.com"
    )


# ---------------------------------------------------------------------------
# PUBLISHER HOSTNAME
# ---------------------------------------------------------------------------
def test_publisher_hostname():
    assert (
        is_publisher_hostname(
            "www.nature.com"
        )
        is True
    )

    assert (
        is_publisher_hostname(
            "www.mdpi.com"
        )
        is True
    )

    assert (
        is_publisher_hostname(
            "arxiv.org"
        )
        is False
    )


# ---------------------------------------------------------------------------
# CLASSIFY DOI
# ---------------------------------------------------------------------------
def test_classify_doi():
    result = (
        classify_access_location(
            "https://doi.org/"
            "10.1016/j.example"
        )
    )

    assert (
        result.location_type
        == AccessLocationType.DOI
    )

    assert (
        result.hostname
        == "doi.org"
    )


# ---------------------------------------------------------------------------
# CLASSIFY ARXIV
# ---------------------------------------------------------------------------
def test_classify_arxiv():
    result = (
        classify_access_location(
            "https://arxiv.org/"
            "pdf/2111.03139"
        )
    )

    assert (
        result.location_type
        == AccessLocationType.REPOSITORY
    )

    assert (
        result.hostname
        == "arxiv.org"
    )


# ---------------------------------------------------------------------------
# CLASSIFY NATURE
# ---------------------------------------------------------------------------
def test_classify_nature():
    result = (
        classify_access_location(
            "https://www.nature.com/"
            "articles/example.pdf"
        )
    )

    assert (
        result.location_type
        == AccessLocationType.PUBLISHER
    )


# ---------------------------------------------------------------------------
# CLASSIFY MDPI
# ---------------------------------------------------------------------------
def test_classify_mdpi():
    result = (
        classify_access_location(
            "https://www.mdpi.com/"
            "2073-4344/15/7/648/pdf"
        )
    )

    assert (
        result.location_type
        == AccessLocationType.PUBLISHER
    )


# ---------------------------------------------------------------------------
# CLASSIFY CELL
# ---------------------------------------------------------------------------
def test_classify_cell():
    result = (
        classify_access_location(
            "http://www.cell.com/"
            "article/example/pdf"
        )
    )

    assert (
        result.location_type
        == AccessLocationType.PUBLISHER
    )


# ---------------------------------------------------------------------------
# CLASSIFY OTHER
# ---------------------------------------------------------------------------
def test_classify_other():
    result = (
        classify_access_location(
            "https://example.org/"
            "article.pdf"
        )
    )

    assert (
        result.location_type
        == AccessLocationType.OTHER
    )


# ---------------------------------------------------------------------------
# CLASSIFY NONE
# ---------------------------------------------------------------------------
def test_classify_none():
    result = (
        classify_access_location(
            None
        )
    )

    assert (
        result.location_type
        == AccessLocationType.UNKNOWN
    )


# ---------------------------------------------------------------------------
# SUBDOMAIN MATCHES PUBLISHER
# ---------------------------------------------------------------------------
def test_subdomain_matches_publisher():
    result = (
        classify_access_location(
            "https://journals.example."
            "sciencedirect.com/"
            "article.pdf"
        )
    )

    assert (
        result.location_type
        == AccessLocationType.PUBLISHER
    )

