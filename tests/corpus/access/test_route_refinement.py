from psk_tmd.corpus.access.models import (
    AcquisitionRoute,
)
from psk_tmd.corpus.access.route_refinement import (
    RouteRefinementBasis,
    refine_acquisition_route,
    select_stable_source_url,
)


# ---------------------------------------------------------------------------
# REQUESTED URL IS STABLE SOURCE
# ---------------------------------------------------------------------------
def test_requested_url_is_stable_source():
    result = (
        select_stable_source_url(
            requested_url=(
                "https://www.nature.com/"
                "article.pdf"
            ),
            final_url=(
                "https://www.nature.com/"
                "article.pdf?"
                "error=cookies_not_supported"
                "&code=temporary"
            ),
        )
    )

    assert (
        result
        == (
            "https://www.nature.com/"
            "article.pdf"
        )
    )


# ---------------------------------------------------------------------------
# FINAL URL IS FALLBACK
# ---------------------------------------------------------------------------
def test_final_url_is_fallback():
    result = (
        select_stable_source_url(
            requested_url=None,
            final_url=(
                "https://example.org/"
                "article.pdf"
            ),
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
# ELSEVIER NONE BECOMES OFFICIAL API
# ---------------------------------------------------------------------------
def test_elsevier_none_becomes_official_api():
    result = (
        refine_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            provider_key="elsevier",
            original_route=(
                AcquisitionRoute.NONE
            ),
            requested_url=(
                "https://doi.org/"
                "10.1016/example"
            ),
            final_url=(
                "https://linkinghub."
                "elsevier.com/example"
            ),
            doi=(
                "10.1016/example"
            ),
        )
    )

    assert (
        result.refined_route
        == AcquisitionRoute.OFFICIAL_API
    )

    assert (
        result.route_changed
        is True
    )

    assert (
        result.basis
        == RouteRefinementBasis.PROVIDER_POLICY
    )

    assert (
        result.requires_endpoint_resolution
        is True
    )


# ---------------------------------------------------------------------------
# ELSEVIER PUBLISHER DOWNLOAD BECOMES API
# ---------------------------------------------------------------------------
def test_elsevier_publisher_download_becomes_api():
    result = (
        refine_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            provider_key="elsevier",
            original_route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            requested_url=(
                "https://www.cell.com/"
                "article/example/pdf"
            ),
            final_url=None,
            doi=(
                "10.1016/example"
            ),
        )
    )

    assert (
        result.refined_route
        == AcquisitionRoute.OFFICIAL_API
    )

    assert (
        result.route_changed
        is True
    )


# ---------------------------------------------------------------------------
# ELSEVIER API NEEDS DOI
# ---------------------------------------------------------------------------
def test_elsevier_without_doi_is_not_refined():
    result = (
        refine_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            provider_key="elsevier",
            original_route=(
                AcquisitionRoute.NONE
            ),
            requested_url=None,
            final_url=None,
            doi=None,
        )
    )

    assert (
        result.refined_route
        == AcquisitionRoute.NONE
    )

    assert (
        result.route_changed
        is False
    )


# ---------------------------------------------------------------------------
# ARXIV REPOSITORY ROUTE IS PRESERVED
# ---------------------------------------------------------------------------
def test_arxiv_repository_route_is_preserved():
    result = (
        refine_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            provider_key="arxiv",
            original_route=(
                AcquisitionRoute.OA_REPOSITORY
            ),
            requested_url=(
                "https://arxiv.org/pdf/1234"
            ),
            final_url=(
                "https://arxiv.org/pdf/1234"
            ),
            doi=(
                "10.1016/example"
            ),
        )
    )

    assert (
        result.refined_route
        == AcquisitionRoute.OA_REPOSITORY
    )

    assert (
        result.route_changed
        is False
    )

    assert (
        result.requires_endpoint_resolution
        is False
    )


# ---------------------------------------------------------------------------
# SPRINGER PUBLISHER ROUTE IS PRESERVED
# ---------------------------------------------------------------------------
def test_springer_publisher_route_is_preserved():
    result = (
        refine_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            provider_key=(
                "springer_nature"
            ),
            original_route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            requested_url=(
                "https://www.nature.com/"
                "article.pdf"
            ),
            final_url=(
                "https://www.nature.com/"
                "article.pdf?"
                "code=temporary"
            ),
            doi=(
                "10.1038/example"
            ),
        )
    )

    assert (
        result.refined_route
        == AcquisitionRoute.PUBLISHER_DOWNLOAD
    )

    assert (
        result.stable_source_url
        == (
            "https://www.nature.com/"
            "article.pdf"
        )
    )


# ---------------------------------------------------------------------------
# MDPI NONE IS NOT INVENTED
# ---------------------------------------------------------------------------
def test_mdpi_none_is_not_invented():
    result = (
        refine_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            provider_key="mdpi",
            original_route=(
                AcquisitionRoute.NONE
            ),
            requested_url=(
                "https://doi.org/"
                "10.3390/example"
            ),
            final_url=None,
            doi=(
                "10.3390/example"
            ),
        )
    )

    assert (
        result.refined_route
        == AcquisitionRoute.NONE
    )

    assert (
        result.basis
        == RouteRefinementBasis.NO_REFINEMENT
    )


# ---------------------------------------------------------------------------
# EXISTING MDPI ROUTE IS PRESERVED
# ---------------------------------------------------------------------------
def test_existing_mdpi_route_is_preserved():
    result = (
        refine_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            provider_key="mdpi",
            original_route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            requested_url=(
                "https://www.mdpi.com/"
                "article/pdf"
            ),
            final_url=None,
            doi=(
                "10.3390/example"
            ),
        )
    )

    assert (
        result.refined_route
        == AcquisitionRoute.PUBLISHER_DOWNLOAD
    )

    assert (
        result.route_changed
        is False
    )

