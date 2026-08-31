from pydantic import (
    BaseModel,
    field_validator,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)
from psk_tmd.corpus.access.location import (
    AccessLocationClassification,
    AccessLocationType,
)
from psk_tmd.corpus.access.models import (
    AcquisitionRoute,
)


# ---------------------------------------------------------------------------
# ACQUISITION ROUTE PROPOSAL
# ---------------------------------------------------------------------------
class AcquisitionRouteProposal(
    BaseModel
):
    access_id: str

    candidate_id: str

    proposed_route: AcquisitionRoute

    location_type: AccessLocationType

    source_url: str | None = None

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
# PROPOSE ACQUISITION ROUTE
# ---------------------------------------------------------------------------
def propose_acquisition_route(
    *,
    access_id: str,
    candidate_id: str,
    classification: AccessLocationClassification,
) -> AcquisitionRouteProposal:
    location_type = (
        classification.location_type
    )

    if (
        location_type
        == AccessLocationType.REPOSITORY
    ):
        return AcquisitionRouteProposal(
            access_id=(
                access_id
            ),
            candidate_id=(
                candidate_id
            ),
            proposed_route=(
                AcquisitionRoute.OA_REPOSITORY
            ),
            location_type=(
                location_type
            ),
            source_url=(
                classification.url
            ),
            reason=(
                "The reported full-text location "
                "is hosted by a recognized "
                "open repository. The route is "
                "proposed but retrieval has not "
                "yet been verified."
            ),
        )

    if (
        location_type
        == AccessLocationType.PUBLISHER
    ):
        return AcquisitionRouteProposal(
            access_id=(
                access_id
            ),
            candidate_id=(
                candidate_id
            ),
            proposed_route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            location_type=(
                location_type
            ),
            source_url=(
                classification.url
            ),
            reason=(
                "The reported full-text location "
                "is hosted on a recognized "
                "publisher domain. The route is "
                "proposed but retrieval and "
                "permission have not yet "
                "been verified."
            ),
        )

    if (
        location_type
        == AccessLocationType.DOI
    ):
        return AcquisitionRouteProposal(
            access_id=(
                access_id
            ),
            candidate_id=(
                candidate_id
            ),
            proposed_route=(
                AcquisitionRoute.NONE
            ),
            location_type=(
                location_type
            ),
            source_url=(
                classification.url
            ),
            reason=(
                "The reported location is only "
                "a DOI resolver. The final "
                "publisher or repository "
                "destination must be resolved "
                "before proposing an acquisition "
                "route."
            ),
        )

    if (
        location_type
        == AccessLocationType.OTHER
    ):
        return AcquisitionRouteProposal(
            access_id=(
                access_id
            ),
            candidate_id=(
                candidate_id
            ),
            proposed_route=(
                AcquisitionRoute.NONE
            ),
            location_type=(
                location_type
            ),
            source_url=(
                classification.url
            ),
            reason=(
                "The reported location is not "
                "recognized as a publisher, "
                "repository, or DOI resolver. "
                "Manual review is required."
            ),
        )

    return AcquisitionRouteProposal(
        access_id=(
            access_id
        ),
        candidate_id=(
            candidate_id
        ),
        proposed_route=(
            AcquisitionRoute.NONE
        ),
        location_type=(
            location_type
        ),
        source_url=(
            classification.url
        ),
        reason=(
            "No usable classified access "
            "location is available, so no "
            "acquisition route can be proposed."
        ),
    )

