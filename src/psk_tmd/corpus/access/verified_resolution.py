from pydantic import (
    BaseModel,
    field_validator,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)
from psk_tmd.corpus.access.location import (
    AccessLocationType,
    classify_access_location,
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


# ---------------------------------------------------------------------------
# VERIFIED ACCESS PROPOSAL
# ---------------------------------------------------------------------------
class VerifiedAccessProposal(
    BaseModel
):
    access_id: str

    candidate_id: str

    proposed_access_status: AccessStatus

    proposed_acquisition_route: AcquisitionRoute

    proposed_tdm_status: TDMStatus

    full_text_available: bool

    full_text_format: FullTextFormat | None = None

    source_url: str | None = None

    final_location_type: AccessLocationType

    reason: str

    @field_validator(
        "access_id",
        "candidate_id",
        "reason",
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str,
    ) -> str:
        normalized = (
            normalize_whitespace(
                value
            )
        )

        if not normalized:
            raise ValueError(
                "Required text field "
                "must not be empty."
            )

        return normalized

    @field_validator(
        "source_url",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = (
            normalize_whitespace(
                value
            )
        )

        return (
            normalized
            or None
        )


# ---------------------------------------------------------------------------
# RESOLVE FINAL ROUTE
# ---------------------------------------------------------------------------
def resolve_final_route(
    route_proposal: AcquisitionRouteProposal,
    verification: URLVerificationResult,
) -> AcquisitionRoute:
    if (
        route_proposal.proposed_route
        != AcquisitionRoute.NONE
    ):
        return (
            route_proposal.proposed_route
        )

    classification = (
        classify_access_location(
            verification.final_url
        )
    )

    if (
        classification.location_type
        == AccessLocationType.REPOSITORY
    ):
        return (
            AcquisitionRoute.OA_REPOSITORY
        )

    if (
        classification.location_type
        == AccessLocationType.PUBLISHER
    ):
        return (
            AcquisitionRoute.PUBLISHER_DOWNLOAD
        )

    return (
        AcquisitionRoute.NONE
    )


# ---------------------------------------------------------------------------
# BUILD VERIFIED ACCESS PROPOSAL
# ---------------------------------------------------------------------------
def build_verified_access_proposal(
    *,
    access_id: str,
    candidate_id: str,
    route_proposal: AcquisitionRouteProposal,
    verification: URLVerificationResult,
) -> VerifiedAccessProposal:
    final_classification = (
        classify_access_location(
            verification.final_url
            or verification.requested_url
        )
    )

    final_route = (
        resolve_final_route(
            route_proposal,
            verification,
        )
    )

    if (
        verification.success
        and verification.appears_pdf
    ):
        return VerifiedAccessProposal(
            access_id=(
                access_id
            ),
            candidate_id=(
                candidate_id
            ),
            proposed_access_status=(
                AccessStatus.AVAILABLE
            ),
            proposed_acquisition_route=(
                final_route
            ),
            proposed_tdm_status=(
                TDMStatus.NOT_EVALUATED
            ),
            full_text_available=True,
            full_text_format=(
                FullTextFormat.PDF
            ),
            source_url=(
                verification.final_url
                or verification.requested_url
            ),
            final_location_type=(
                final_classification.location_type
            ),
            reason=(
                "URL verification returned content "
                "identified as PDF. Full-text "
                "retrievability is therefore verified, "
                "but TDM permission has not yet "
                "been evaluated."
            ),
        )

    if (
        verification.success
        and verification.appears_html
    ):
        return VerifiedAccessProposal(
            access_id=(
                access_id
            ),
            candidate_id=(
                candidate_id
            ),
            proposed_access_status=(
                AccessStatus.REQUIRES_REVIEW
            ),
            proposed_acquisition_route=(
                final_route
            ),
            proposed_tdm_status=(
                TDMStatus.NOT_EVALUATED
            ),
            full_text_available=False,
            source_url=(
                verification.final_url
                or verification.requested_url
            ),
            final_location_type=(
                final_classification.location_type
            ),
            reason=(
                "The URL is reachable but returned "
                "HTML rather than verified full-text "
                "content. Further access resolution "
                "is required."
            ),
        )

    if not verification.success:
        return VerifiedAccessProposal(
            access_id=(
                access_id
            ),
            candidate_id=(
                candidate_id
            ),
            proposed_access_status=(
                AccessStatus.REQUIRES_REVIEW
            ),
            proposed_acquisition_route=(
                final_route
            ),
            proposed_tdm_status=(
                TDMStatus.NOT_EVALUATED
            ),
            full_text_available=False,
            source_url=(
                verification.requested_url
            ),
            final_location_type=(
                final_classification.location_type
            ),
            reason=(
                "URL verification did not succeed. "
                "The failure does not establish that "
                "the work is unavailable, so manual "
                "or alternative permitted access "
                "resolution is still required."
            ),
        )

    return VerifiedAccessProposal(
        access_id=(
            access_id
        ),
        candidate_id=(
            candidate_id
        ),
        proposed_access_status=(
            AccessStatus.REQUIRES_REVIEW
        ),
        proposed_acquisition_route=(
            final_route
        ),
        proposed_tdm_status=(
            TDMStatus.NOT_EVALUATED
        ),
        full_text_available=False,
        source_url=(
            verification.final_url
            or verification.requested_url
        ),
        final_location_type=(
            final_classification.location_type
        ),
        reason=(
            "The URL request succeeded but the "
            "returned content was neither verified "
            "PDF nor recognized HTML."
        ),
    )

