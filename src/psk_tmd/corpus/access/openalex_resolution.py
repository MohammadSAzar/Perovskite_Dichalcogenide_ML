from psk_tmd.corpus.access.evidence import (
    AccessEvidenceRecord,
    AccessEvidenceType,
)
from psk_tmd.corpus.access.models import (
    AccessRecord,
    AccessStatus,
    AcquisitionRoute,
    TDMStatus,
)
from psk_tmd.corpus.access.resolution import (
    AccessResolutionResult,
    build_access_resolution_result,
)


# ---------------------------------------------------------------------------
# GET EVIDENCE BY TYPE
# ---------------------------------------------------------------------------
def get_evidence_by_type(
    evidence_records: list[
        AccessEvidenceRecord
    ]
    | tuple[
        AccessEvidenceRecord,
        ...
    ],
    evidence_type: AccessEvidenceType,
) -> tuple[
    AccessEvidenceRecord,
    ...
]:
    return tuple(
        evidence
        for evidence in evidence_records
        if (
            evidence.evidence_type
            == evidence_type
        )
    )


# ---------------------------------------------------------------------------
# GET SINGLE EVIDENCE
# ---------------------------------------------------------------------------
def get_single_evidence(
    evidence_records: list[
        AccessEvidenceRecord
    ]
    | tuple[
        AccessEvidenceRecord,
        ...
    ],
    evidence_type: AccessEvidenceType,
) -> AccessEvidenceRecord | None:
    matches = (
        get_evidence_by_type(
            evidence_records,
            evidence_type,
        )
    )

    if len(
        matches
    ) > 1:
        raise ValueError(
            "Expected at most one "
            f"{evidence_type.value} evidence "
            "record per OpenAlex lookup."
        )

    if not matches:
        return None

    return matches[
        0
    ]


# ---------------------------------------------------------------------------
# NORMALIZE OA STATUS
# ---------------------------------------------------------------------------
def normalize_oa_status(
    evidence: AccessEvidenceRecord | None,
) -> str | None:
    if (
        evidence is None
        or evidence.value is None
    ):
        return None

    normalized = (
        evidence.value
        .strip()
        .lower()
    )

    return (
        normalized
        or None
    )


# ---------------------------------------------------------------------------
# PROPOSE OPENALEX RESOLUTION
# ---------------------------------------------------------------------------
def propose_openalex_resolution(
    access_record: AccessRecord,
    evidence_records: list[
        AccessEvidenceRecord
    ]
    | tuple[
        AccessEvidenceRecord,
        ...
    ],
) -> AccessResolutionResult:
    oa_evidence = (
        get_single_evidence(
            evidence_records,
            AccessEvidenceType.OA_STATUS,
        )
    )

    location_evidence = (
        get_single_evidence(
            evidence_records,
            AccessEvidenceType.FULL_TEXT_LOCATION,
        )
    )

    version_evidence = (
        get_single_evidence(
            evidence_records,
            AccessEvidenceType.VERSION,
        )
    )

    oa_status = (
        normalize_oa_status(
            oa_evidence
        )
    )

    source_url = None

    if location_evidence is not None:
        source_url = (
            location_evidence.source_url
        )

    source_version = None

    if version_evidence is not None:
        source_version = (
            version_evidence.value
        )

    if oa_status == "closed":
        return (
            build_access_resolution_result(
                access_record,
                evidence_records,
                proposed_access_status=(
                    AccessStatus.METADATA_ONLY
                ),
                proposed_acquisition_route=(
                    AcquisitionRoute.NONE
                ),
                proposed_tdm_status=(
                    TDMStatus.NOT_EVALUATED
                ),
                reason=(
                    "OpenAlex reports the work "
                    "as closed and provides no "
                    "verified open full-text access."
                ),
            )
        )

    if (
        oa_status
        in {
            "bronze",
            "diamond",
            "gold",
            "green",
            "hybrid",
        }
        and location_evidence is not None
    ):
        return (
            build_access_resolution_result(
                access_record,
                evidence_records,
                proposed_access_status=(
                    AccessStatus.REQUIRES_REVIEW
                ),
                proposed_acquisition_route=(
                    AcquisitionRoute.NONE
                ),
                proposed_tdm_status=(
                    TDMStatus.NOT_EVALUATED
                ),
                proposed_source_url=(
                    source_url
                ),
                proposed_source_version=(
                    source_version
                ),
                reason=(
                    "OpenAlex reports a non-closed "
                    "OA status and an open-access "
                    "location. The location has not "
                    "yet been independently verified "
                    "for retrieval or TDM permission."
                ),
            )
        )

    return (
        build_access_resolution_result(
            access_record,
            evidence_records,
            proposed_access_status=(
                AccessStatus.REQUIRES_REVIEW
            ),
            proposed_acquisition_route=(
                AcquisitionRoute.NONE
            ),
            proposed_tdm_status=(
                TDMStatus.NOT_EVALUATED
            ),
            proposed_source_url=(
                source_url
            ),
            proposed_source_version=(
                source_version
            ),
            reason=(
                "OpenAlex evidence is incomplete "
                "or does not support a deterministic "
                "access classification."
            ),
        )
    )

