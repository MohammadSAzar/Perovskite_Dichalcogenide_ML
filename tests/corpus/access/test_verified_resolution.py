from psk_tmd.corpus.access.location import (
    AccessLocationType,
)
from psk_tmd.corpus.access.models import (
    AccessStatus,
    AcquisitionRoute,
    FullTextFormat,
    TDMStatus,
)
from psk_tmd.corpus.access.route_proposal import (
    AcquisitionRouteProposal,
)
from psk_tmd.corpus.access.url_verification import (
    URLVerificationResult,
)
from psk_tmd.corpus.access.verified_resolution import (
    build_verified_access_proposal,
    resolve_final_route,
)


# ---------------------------------------------------------------------------
# MAKE ROUTE PROPOSAL
# ---------------------------------------------------------------------------
def make_route_proposal(
    route: AcquisitionRoute,
) -> AcquisitionRouteProposal:
    return AcquisitionRouteProposal(
        access_id="ACC-000001",
        candidate_id="CND-000001",
        proposed_route=(
            route
        ),
        location_type=(
            AccessLocationType.PUBLISHER
        ),
        source_url=(
            "https://example.org/article.pdf"
        ),
        reason="Test route.",
    )


# ---------------------------------------------------------------------------
# VERIFIED PDF BECOMES AVAILABLE
# ---------------------------------------------------------------------------
def test_verified_pdf_becomes_available():
    verification = URLVerificationResult(
        requested_url=(
            "https://www.nature.com/article.pdf"
        ),
        success=True,
        status_code=200,
        final_url=(
            "https://www.nature.com/article.pdf"
        ),
        content_type="application/pdf",
        appears_pdf=True,
    )

    result = (
        build_verified_access_proposal(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route_proposal=(
                make_route_proposal(
                    AcquisitionRoute.PUBLISHER_DOWNLOAD
                )
            ),
            verification=(
                verification
            ),
        )
    )

    assert (
        result.proposed_access_status
        == AccessStatus.AVAILABLE
    )

    assert (
        result.full_text_available
        is True
    )

    assert (
        result.full_text_format
        == FullTextFormat.PDF
    )

    assert (
        result.proposed_tdm_status
        == TDMStatus.NOT_EVALUATED
    )


# ---------------------------------------------------------------------------
# HTML REMAINS REVIEW
# ---------------------------------------------------------------------------
def test_html_remains_review():
    verification = URLVerificationResult(
        requested_url=(
            "https://doi.org/10.1000/example"
        ),
        success=True,
        status_code=200,
        final_url=(
            "https://linkinghub.elsevier.com/example"
        ),
        content_type="text/html",
        appears_html=True,
    )

    result = (
        build_verified_access_proposal(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route_proposal=(
                make_route_proposal(
                    AcquisitionRoute.NONE
                )
            ),
            verification=(
                verification
            ),
        )
    )

    assert (
        result.proposed_access_status
        == AccessStatus.REQUIRES_REVIEW
    )

    assert (
        result.full_text_available
        is False
    )

    assert (
        result.proposed_acquisition_route
        == AcquisitionRoute.PUBLISHER_DOWNLOAD
    )


# ---------------------------------------------------------------------------
# HTTP FAILURE REMAINS REVIEW
# ---------------------------------------------------------------------------
def test_http_failure_remains_review():
    verification = URLVerificationResult(
        requested_url=(
            "https://www.mdpi.com/article.pdf"
        ),
        success=False,
        error_type="HTTPError",
        error_message="HTTP Error 403: Forbidden",
    )

    result = (
        build_verified_access_proposal(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route_proposal=(
                make_route_proposal(
                    AcquisitionRoute.PUBLISHER_DOWNLOAD
                )
            ),
            verification=(
                verification
            ),
        )
    )

    assert (
        result.proposed_access_status
        == AccessStatus.REQUIRES_REVIEW
    )

    assert (
        result.full_text_available
        is False
    )

    assert (
        result.proposed_tdm_status
        == TDMStatus.NOT_EVALUATED
    )


# ---------------------------------------------------------------------------
# DOI REDIRECT CAN RESOLVE PUBLISHER ROUTE
# ---------------------------------------------------------------------------
def test_doi_redirect_can_resolve_publisher_route():
    verification = URLVerificationResult(
        requested_url=(
            "https://doi.org/10.1000/example"
        ),
        success=True,
        final_url=(
            "https://linkinghub.elsevier.com/example"
        ),
        content_type="text/html",
        appears_html=True,
    )

    route = (
        resolve_final_route(
            make_route_proposal(
                AcquisitionRoute.NONE
            ),
            verification,
        )
    )

    assert (
        route
        == AcquisitionRoute.PUBLISHER_DOWNLOAD
    )


# ---------------------------------------------------------------------------
# REPOSITORY ROUTE IS PRESERVED
# ---------------------------------------------------------------------------
def test_repository_route_is_preserved():
    proposal = AcquisitionRouteProposal(
        access_id="ACC-000001",
        candidate_id="CND-000001",
        proposed_route=(
            AcquisitionRoute.OA_REPOSITORY
        ),
        location_type=(
            AccessLocationType.REPOSITORY
        ),
        source_url=(
            "https://arxiv.org/pdf/1234"
        ),
        reason="Repository.",
    )

    verification = URLVerificationResult(
        requested_url=(
            "https://arxiv.org/pdf/1234"
        ),
        success=True,
        final_url=(
            "https://arxiv.org/pdf/1234"
        ),
        content_type="application/pdf",
        appears_pdf=True,
    )

    result = (
        build_verified_access_proposal(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route_proposal=(
                proposal
            ),
            verification=(
                verification
            ),
        )
    )

    assert (
        result.proposed_acquisition_route
        == AcquisitionRoute.OA_REPOSITORY
    )

    assert (
        result.final_location_type
        == AccessLocationType.REPOSITORY
    )

