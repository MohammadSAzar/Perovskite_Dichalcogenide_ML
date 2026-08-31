from psk_tmd.corpus.access.location import (
    AccessLocationClassification,
    AccessLocationType,
)
from psk_tmd.corpus.access.models import (
    AcquisitionRoute,
)
from psk_tmd.corpus.access.route_proposal import (
    propose_acquisition_route,
)


# ---------------------------------------------------------------------------
# REPOSITORY PROPOSES OA REPOSITORY
# ---------------------------------------------------------------------------
def test_repository_proposes_oa_repository():
    classification = (
        AccessLocationClassification(
            location_type=(
                AccessLocationType.REPOSITORY
            ),
            url=(
                "https://arxiv.org/pdf/1234"
            ),
            hostname="arxiv.org",
            reason="Repository.",
        )
    )

    proposal = (
        propose_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            classification=(
                classification
            ),
        )
    )

    assert (
        proposal.proposed_route
        == AcquisitionRoute.OA_REPOSITORY
    )


# ---------------------------------------------------------------------------
# PUBLISHER PROPOSES PUBLISHER DOWNLOAD
# ---------------------------------------------------------------------------
def test_publisher_proposes_publisher_download():
    classification = (
        AccessLocationClassification(
            location_type=(
                AccessLocationType.PUBLISHER
            ),
            url=(
                "https://www.mdpi.com/"
                "article.pdf"
            ),
            hostname="www.mdpi.com",
            reason="Publisher.",
        )
    )

    proposal = (
        propose_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            classification=(
                classification
            ),
        )
    )

    assert (
        proposal.proposed_route
        == AcquisitionRoute.PUBLISHER_DOWNLOAD
    )


# ---------------------------------------------------------------------------
# DOI PROPOSES NONE
# ---------------------------------------------------------------------------
def test_doi_proposes_none():
    classification = (
        AccessLocationClassification(
            location_type=(
                AccessLocationType.DOI
            ),
            url=(
                "https://doi.org/"
                "10.1000/example"
            ),
            hostname="doi.org",
            reason="DOI.",
        )
    )

    proposal = (
        propose_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            classification=(
                classification
            ),
        )
    )

    assert (
        proposal.proposed_route
        == AcquisitionRoute.NONE
    )


# ---------------------------------------------------------------------------
# OTHER PROPOSES NONE
# ---------------------------------------------------------------------------
def test_other_proposes_none():
    classification = (
        AccessLocationClassification(
            location_type=(
                AccessLocationType.OTHER
            ),
            url=(
                "https://example.org/file.pdf"
            ),
            hostname="example.org",
            reason="Other.",
        )
    )

    proposal = (
        propose_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            classification=(
                classification
            ),
        )
    )

    assert (
        proposal.proposed_route
        == AcquisitionRoute.NONE
    )


# ---------------------------------------------------------------------------
# UNKNOWN PROPOSES NONE
# ---------------------------------------------------------------------------
def test_unknown_proposes_none():
    classification = (
        AccessLocationClassification(
            location_type=(
                AccessLocationType.UNKNOWN
            ),
            reason="Unknown.",
        )
    )

    proposal = (
        propose_acquisition_route(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            classification=(
                classification
            ),
        )
    )

    assert (
        proposal.proposed_route
        == AcquisitionRoute.NONE
    )


# ---------------------------------------------------------------------------
# LINKAGE IS PRESERVED
# ---------------------------------------------------------------------------
def test_linkage_is_preserved():
    classification = (
        AccessLocationClassification(
            location_type=(
                AccessLocationType.REPOSITORY
            ),
            url=(
                "https://arxiv.org/pdf/1234"
            ),
            hostname="arxiv.org",
            reason="Repository.",
        )
    )

    proposal = (
        propose_acquisition_route(
            access_id="ACC-000123",
            candidate_id="CND-000456",
            classification=(
                classification
            ),
        )
    )

    assert (
        proposal.access_id
        == "ACC-000123"
    )

    assert (
        proposal.candidate_id
        == "CND-000456"
    )

    assert (
        proposal.source_url
        == "https://arxiv.org/pdf/1234"
    )


