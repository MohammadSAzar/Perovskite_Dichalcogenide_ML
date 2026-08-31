from dataclasses import (
    dataclass,
)
from datetime import (
    date,
)
import time

from psk_tmd.corpus.access.evidence import (
    AccessEvidenceRecord,
)
from psk_tmd.corpus.access.models import (
    AccessRecord,
)
from psk_tmd.corpus.access.openalex import (
    resolve_openalex_evidence,
)


# ---------------------------------------------------------------------------
# OPENALEX CALL RESULT
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class OpenAlexAccessCallResult:
    access_id: str

    candidate_id: str

    doi: str | None

    success: bool

    evidence_records: tuple[
        AccessEvidenceRecord,
        ...
    ]

    error_type: str | None = None

    error_message: str | None = None


# ---------------------------------------------------------------------------
# OPENALEX RUN RESULT
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class OpenAlexAccessRunResult:
    call_results: tuple[
        OpenAlexAccessCallResult,
        ...
    ]

    evidence_records: tuple[
        AccessEvidenceRecord,
        ...
    ]

    attempted_calls: int

    successful_calls: int

    failed_calls: int


# ---------------------------------------------------------------------------
# RUN OPENALEX ACCESS LOOKUPS
# ---------------------------------------------------------------------------
def run_openalex_access_lookups(
    access_records: list[
        AccessRecord
    ]
    | tuple[
        AccessRecord,
        ...
    ],
    *,
    observed_date: date,
    start_evidence_index: int = 1,
    delay_seconds: float = 1.0,
    timeout: float = 30.0,
    api_key: str | None = None,
) -> OpenAlexAccessRunResult:
    if start_evidence_index < 1:
        raise ValueError(
            "start_evidence_index "
            "must be at least 1."
        )

    if delay_seconds < 0:
        raise ValueError(
            "delay_seconds "
            "must not be negative."
        )

    if timeout <= 0:
        raise ValueError(
            "timeout must be "
            "greater than zero."
        )

    call_results = []

    all_evidence = []

    attempted_calls = 0

    successful_calls = 0

    failed_calls = 0

    next_evidence_index = (
        start_evidence_index
    )

    for access_record in access_records:
        attempted_calls += 1

        try:
            evidence_records = (
                resolve_openalex_evidence(
                    access_record,
                    start_index=(
                        next_evidence_index
                    ),
                    observed_date=(
                        observed_date
                    ),
                    api_key=(
                        api_key
                    ),
                    timeout=(
                        timeout
                    ),
                )
            )

        except Exception as exc:
            failed_calls += 1

            call_results.append(
                OpenAlexAccessCallResult(
                    access_id=(
                        access_record.access_id
                    ),
                    candidate_id=(
                        access_record.candidate_id
                    ),
                    doi=(
                        access_record.doi
                    ),
                    success=False,
                    evidence_records=(),
                    error_type=(
                        type(
                            exc
                        ).__name__
                    ),
                    error_message=(
                        str(
                            exc
                        )
                    ),
                )
            )

        else:
            successful_calls += 1

            evidence_tuple = tuple(
                evidence_records
            )

            call_results.append(
                OpenAlexAccessCallResult(
                    access_id=(
                        access_record.access_id
                    ),
                    candidate_id=(
                        access_record.candidate_id
                    ),
                    doi=(
                        access_record.doi
                    ),
                    success=True,
                    evidence_records=(
                        evidence_tuple
                    ),
                )
            )

            all_evidence.extend(
                evidence_records
            )

            next_evidence_index += len(
                evidence_records
            )

        if delay_seconds > 0:
            time.sleep(
                delay_seconds
            )

    return OpenAlexAccessRunResult(
        call_results=tuple(
            call_results
        ),
        evidence_records=tuple(
            all_evidence
        ),
        attempted_calls=(
            attempted_calls
        ),
        successful_calls=(
            successful_calls
        ),
        failed_calls=(
            failed_calls
        ),
    )

