import pytest

from psk_tmd.corpus.access.elsevier_api import (
    ELSEVIER_API_KEY_HEADER,
    ELSEVIER_DEFAULT_ACCEPT,
    build_elsevier_article_api_request,
    build_elsevier_article_doi_endpoint,
    build_elsevier_full_text_url,
    normalize_elsevier_doi,
)


# ---------------------------------------------------------------------------
# NORMALIZE RAW DOI
# ---------------------------------------------------------------------------
def test_normalize_raw_doi():
    assert (
        normalize_elsevier_doi(
            "10.1016/j.example.2026.001"
        )
        == "10.1016/j.example.2026.001"
    )


# ---------------------------------------------------------------------------
# NORMALIZE DOI URL
# ---------------------------------------------------------------------------
def test_normalize_doi_url():
    assert (
        normalize_elsevier_doi(
            (
                "https://doi.org/"
                "10.1016/j.example.2026.001"
            )
        )
        == "10.1016/j.example.2026.001"
    )


# ---------------------------------------------------------------------------
# NORMALIZE DOI PREFIX
# ---------------------------------------------------------------------------
def test_normalize_doi_prefix():
    assert (
        normalize_elsevier_doi(
            (
                "DOI: "
                "10.1016/j.example.2026.001"
            )
        )
        == "10.1016/j.example.2026.001"
    )


# ---------------------------------------------------------------------------
# EMPTY DOI IS REJECTED
# ---------------------------------------------------------------------------
def test_empty_doi_is_rejected():
    with pytest.raises(
        ValueError,
    ):
        normalize_elsevier_doi(
            "   "
        )


# ---------------------------------------------------------------------------
# BUILD DOI ENDPOINT
# ---------------------------------------------------------------------------
def test_build_doi_endpoint():
    result = (
        build_elsevier_article_doi_endpoint(
            "10.1016/j.example.2026.001"
        )
    )

    assert (
        result
        == (
            "https://api.elsevier.com/"
            "content/article/doi/"
            "10.1016%2Fj.example.2026.001"
        )
    )


# ---------------------------------------------------------------------------
# BUILD FULL TEXT URL
# ---------------------------------------------------------------------------
def test_build_full_text_url():
    result = (
        build_elsevier_full_text_url(
            "10.1016/j.example.2026.001"
        )
    )

    assert (
        result
        == (
            "https://api.elsevier.com/"
            "content/article/doi/"
            "10.1016%2Fj.example.2026.001"
            "?view=FULL"
        )
    )


# ---------------------------------------------------------------------------
# BUILD ARTICLE API REQUEST
# ---------------------------------------------------------------------------
def test_build_article_api_request():
    request = (
        build_elsevier_article_api_request(
            "10.1016/j.example.2026.001"
        )
    )

    assert (
        request.doi
        == "10.1016/j.example.2026.001"
    )

    assert (
        request.accept
        == ELSEVIER_DEFAULT_ACCEPT
    )

    assert (
        request.accept
        == "text/xml"
    )

    assert (
        request.view
        == "FULL"
    )

    assert (
        request.requires_api_key
        is True
    )

    assert (
        request.api_key_header
        == ELSEVIER_API_KEY_HEADER
    )

    assert (
        request.api_key_header
        == "X-ELS-APIKey"
    )

    assert (
        request.requires_entitlement_check
        is True
    )


# ---------------------------------------------------------------------------
# API KEY IS NOT EMBEDDED IN URL
# ---------------------------------------------------------------------------
def test_api_key_is_not_embedded_in_url():
    request = (
        build_elsevier_article_api_request(
            "10.1016/j.example.2026.001"
        )
    )

    lowered = (
        request.endpoint_url.lower()
    )

    assert (
        "apikey="
        not in lowered
    )

    assert (
        "api_key="
        not in lowered
    )

