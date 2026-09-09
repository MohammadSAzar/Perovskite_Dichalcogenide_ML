from enum import (
    Enum,
)

from pydantic import (
    BaseModel,
    field_validator,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)
from psk_tmd.corpus.access.models import (
    AcquisitionRoute,
)


# ---------------------------------------------------------------------------
# ROUTE REFINEMENT BASIS
# ---------------------------------------------------------------------------
class RouteRefinementBasis(
    str,
    Enum,
):
    EXISTING_ROUTE = (
        "existing_route"
    )

    PROVIDER_POLICY = (
        "provider_policy"
    )

    NO_REFINEMENT = (
        "no_refinement"
    )


# ---------------------------------------------------------------------------
# ROUTE REFINEMENT RESULT
# ---------------------------------------------------------------------------
class RouteRefinementResult(
    BaseModel
):
    access_id: str

    candidate_id: str

    provider_key: str | None = None

    original_route: AcquisitionRoute

    refined_route: AcquisitionRoute

    route_changed: bool

    basis: RouteRefinementBasis

    stable_source_url: str | None = None

    observed_final_url: str | None = None

    doi: str | None = None

    requires_endpoint_resolution: bool

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
                "Required route refinement "
                "field must not be empty."
            )

        return normalized

    @field_validator(
        "provider_key",
        "stable_source_url",
        "observed_final_url",
        "doi",
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
# SELECT STABLE SOURCE URL
# ---------------------------------------------------------------------------
def select_stable_source_url(
    *,
    requested_url: str | None,
    final_url: str | None,
) -> str | None:
    if requested_url is not None:
        normalized_requested = (
            normalize_whitespace(
                requested_url
            )
        )

        if normalized_requested:
            return (
                normalized_requested
            )

    if final_url is not None:
        normalized_final = (
            normalize_whitespace(
                final_url
            )
        )

        if normalized_final:
            return (
                normalized_final
            )

    return None


# ---------------------------------------------------------------------------
# REFINE ACQUISITION ROUTE
# ---------------------------------------------------------------------------
def refine_acquisition_route(
    *,
    access_id: str,
    candidate_id: str,
    provider_key: str | None,
    original_route: AcquisitionRoute,
    requested_url: str | None,
    final_url: str | None,
    doi: str | None,
) -> RouteRefinementResult:
    stable_source_url = (
        select_stable_source_url(
            requested_url=(
                requested_url
            ),
            final_url=(
                final_url
            ),
        )
    )

    if (
        provider_key
        == "elsevier"
        and doi is not None
    ):
        return RouteRefinementResult(
            access_id=(
                access_id
            ),
            candidate_id=(
                candidate_id
            ),
            provider_key=(
                provider_key
            ),
            original_route=(
                original_route
            ),
            refined_route=(
                AcquisitionRoute.OFFICIAL_API
            ),
            route_changed=(
                original_route
                != AcquisitionRoute.OFFICIAL_API
            ),
            basis=(
                RouteRefinementBasis.PROVIDER_POLICY
            ),
            stable_source_url=(
                stable_source_url
            ),
            observed_final_url=(
                final_url
            ),
            doi=(
                doi
            ),
            requires_endpoint_resolution=True,
            reason=(
                "Elsevier provider-policy "
                "evidence identifies the "
                "official API as the supported "
                "automated TDM route. The "
                "article DOI is available, but "
                "the concrete API endpoint has "
                "not yet been resolved."
            ),
        )

    if (
        original_route
        != AcquisitionRoute.NONE
    ):
        return RouteRefinementResult(
            access_id=(
                access_id
            ),
            candidate_id=(
                candidate_id
            ),
            provider_key=(
                provider_key
            ),
            original_route=(
                original_route
            ),
            refined_route=(
                original_route
            ),
            route_changed=False,
            basis=(
                RouteRefinementBasis.EXISTING_ROUTE
            ),
            stable_source_url=(
                stable_source_url
            ),
            observed_final_url=(
                final_url
            ),
            doi=(
                doi
            ),
            requires_endpoint_resolution=False,
            reason=(
                "The existing acquisition "
                "route is preserved because "
                "no evidence-supported route "
                "refinement is required."
            ),
        )

    return RouteRefinementResult(
        access_id=(
            access_id
        ),
        candidate_id=(
            candidate_id
        ),
        provider_key=(
            provider_key
        ),
        original_route=(
            original_route
        ),
        refined_route=(
            AcquisitionRoute.NONE
        ),
        route_changed=False,
        basis=(
            RouteRefinementBasis.NO_REFINEMENT
        ),
        stable_source_url=(
            stable_source_url
        ),
        observed_final_url=(
            final_url
        ),
        doi=(
            doi
        ),
        requires_endpoint_resolution=False,
        reason=(
            "No evidence-supported alternative "
            "acquisition route has been "
            "resolved for this provider."
        ),
    )

