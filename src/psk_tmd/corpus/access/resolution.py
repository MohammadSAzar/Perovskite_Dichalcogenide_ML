from pydantic import (
    BaseModel,
    field_validator,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)
from psk_tmd.corpus.access.evidence import (
    AccessEvidenceRecord,
)
from psk_tmd.corpus.access.models import (
    AccessRecord,
    AccessStatus,
    AcquisitionRoute,
    FullTextFormat,
    TDMStatus,
)


# ---------------------------------------------------------------------------
# ACCESS RESOLUTION RESULT
# ---------------------------------------------------------------------------
class AccessResolutionResult(
    BaseModel
):
    access_id: str

    candidate_id: str

    proposed_access_status: AccessStatus

    proposed_acquisition_route: AcquisitionRoute

    proposed_tdm_status: TDMStatus

    proposed_source_url: str | None = None

    proposed_source_version: str | None = None

    proposed_full_text_available: bool = False

    proposed_full_text_format: FullTextFormat | None = None

    evidence_ids: tuple[
        str,
        ...
    ] = ()

    reason: str

    notes: str | None = None

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
        "proposed_source_url",
        "proposed_source_version",
        "notes",
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

        if not normalized:
            return None

        return normalized

    @field_validator(
        "evidence_ids",
    )
    @classmethod
    def validate_evidence_ids(
        cls,
        value: tuple[
            str,
            ...
        ],
    ) -> tuple[
        str,
        ...
    ]:
        normalized_ids = []

        for evidence_id in value:
            normalized = (
                normalize_whitespace(
                    evidence_id
                )
            )

            if not normalized:
                raise ValueError(
                    "Evidence ID "
                    "must not be empty."
                )

            normalized_ids.append(
                normalized
            )

        if (
            len(
                normalized_ids
            )
            != len(
                set(
                    normalized_ids
                )
            )
        ):
            raise ValueError(
                "Evidence IDs "
                "must be unique."
            )

        return tuple(
            normalized_ids
        )

    @field_validator(
        "proposed_full_text_format",
    )
    @classmethod
    def validate_full_text_format(
        cls,
        value: FullTextFormat | None,
        info,
    ) -> FullTextFormat | None:
        if (
            value is not None
            and not info.data.get(
                "proposed_full_text_available",
                False,
            )
        ):
            raise ValueError(
                "proposed_full_text_format "
                "requires "
                "proposed_full_text_available=True."
            )

        return value


# ---------------------------------------------------------------------------
# VALIDATE EVIDENCE LINKAGE
# ---------------------------------------------------------------------------
def validate_evidence_linkage(
    access_record: AccessRecord,
    evidence_records: list[
        AccessEvidenceRecord
    ]
    | tuple[
        AccessEvidenceRecord,
        ...
    ],
) -> None:
    for evidence in evidence_records:
        if (
            evidence.access_id
            != access_record.access_id
        ):
            raise ValueError(
                "Access evidence access_id "
                "does not match "
                "the access record."
            )

        if (
            evidence.candidate_id
            != access_record.candidate_id
        ):
            raise ValueError(
                "Access evidence candidate_id "
                "does not match "
                "the access record."
            )


# ---------------------------------------------------------------------------
# GET EVIDENCE IDS
# ---------------------------------------------------------------------------
def get_evidence_ids(
    evidence_records: list[
        AccessEvidenceRecord
    ]
    | tuple[
        AccessEvidenceRecord,
        ...
    ],
) -> tuple[
    str,
    ...
]:
    evidence_ids = [
        evidence.evidence_id
        for evidence in evidence_records
    ]

    if (
        len(
            evidence_ids
        )
        != len(
            set(
                evidence_ids
            )
        )
    ):
        raise ValueError(
            "Duplicate access evidence IDs "
            "were provided."
        )

    return tuple(
        evidence_ids
    )


# ---------------------------------------------------------------------------
# BUILD ACCESS RESOLUTION RESULT
# ---------------------------------------------------------------------------
def build_access_resolution_result(
    access_record: AccessRecord,
    evidence_records: list[
        AccessEvidenceRecord
    ]
    | tuple[
        AccessEvidenceRecord,
        ...
    ],
    *,
    proposed_access_status: AccessStatus,
    proposed_acquisition_route: AcquisitionRoute,
    proposed_tdm_status: TDMStatus,
    reason: str,
    proposed_source_url: str | None = None,
    proposed_source_version: str | None = None,
    proposed_full_text_available: bool = False,
    proposed_full_text_format: FullTextFormat | None = None,
    notes: str | None = None,
) -> AccessResolutionResult:
    validate_evidence_linkage(
        access_record,
        evidence_records,
    )

    evidence_ids = (
        get_evidence_ids(
            evidence_records
        )
    )

    return AccessResolutionResult(
        access_id=(
            access_record.access_id
        ),
        candidate_id=(
            access_record.candidate_id
        ),
        proposed_access_status=(
            proposed_access_status
        ),
        proposed_acquisition_route=(
            proposed_acquisition_route
        ),
        proposed_tdm_status=(
            proposed_tdm_status
        ),
        proposed_source_url=(
            proposed_source_url
        ),
        proposed_source_version=(
            proposed_source_version
        ),
        proposed_full_text_available=(
            proposed_full_text_available
        ),
        proposed_full_text_format=(
            proposed_full_text_format
        ),
        evidence_ids=(
            evidence_ids
        ),
        reason=(
            reason
        ),
        notes=(
            notes
        ),
    )

