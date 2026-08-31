import json

from datetime import (
    date,
)
from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.models import (
    AccessRecord,
)
from psk_tmd.corpus.access.openalex_runner import (
    OpenAlexAccessCallResult,
    run_openalex_access_lookups,
)


# ---------------------------------------------------------------------------
# INPUT / OUTPUT CONFIGURATION
# ---------------------------------------------------------------------------
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
    / "initial_access_records.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
)

EVIDENCE_PATH = (
    OUTPUT_DIR
    / "openalex_access_evidence.json"
)

CALL_RESULTS_PATH = (
    OUTPUT_DIR
    / "openalex_access_call_results.json"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "openalex_access_summary.json"
)

DELAY_SECONDS = 1.0

TIMEOUT_SECONDS = 30.0


# ---------------------------------------------------------------------------
# LOAD JSON
# ---------------------------------------------------------------------------
def load_json(
    path: Path,
):
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


# ---------------------------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------------------------
def save_json(
    path: Path,
    payload,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# LOAD ACCESS RECORDS
# ---------------------------------------------------------------------------
def load_access_records(
    path: Path,
) -> list[
    AccessRecord
]:
    payloads = (
        load_json(
            path
        )
    )

    return [
        AccessRecord.model_validate(
            payload
        )
        for payload in payloads
    ]


# ---------------------------------------------------------------------------
# SERIALIZE CALL RESULT
# ---------------------------------------------------------------------------
def serialize_call_result(
    result: OpenAlexAccessCallResult,
) -> dict:
    return {
        "access_id": (
            result.access_id
        ),
        "candidate_id": (
            result.candidate_id
        ),
        "doi": (
            result.doi
        ),
        "success": (
            result.success
        ),
        "evidence_ids": [
            evidence.evidence_id
            for evidence
            in result.evidence_records
        ],
        "evidence_count": (
            len(
                result.evidence_records
            )
        ),
        "error_type": (
            result.error_type
        ),
        "error_message": (
            result.error_message
        ),
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    access_records = (
        load_access_records(
            INPUT_PATH
        )
    )

    observed_date = (
        date.today()
    )

    print(
        "PILOT OPENALEX ACCESS COLLECTION"
    )
    print(
        "=" * 120
    )

    print(
        f"input_records="
        f"{len(access_records)}"
    )

    print(
        f"observed_date="
        f"{observed_date.isoformat()}"
    )

    print(
        f"delay_seconds="
        f"{DELAY_SECONDS}"
    )

    print(
        f"timeout_seconds="
        f"{TIMEOUT_SECONDS}"
    )

    print()

    print(
        "Running OpenAlex access lookups..."
    )

    result = (
        run_openalex_access_lookups(
            access_records,
            observed_date=(
                observed_date
            ),
            start_evidence_index=1,
            delay_seconds=(
                DELAY_SECONDS
            ),
            timeout=(
                TIMEOUT_SECONDS
            ),
        )
    )

    evidence_payload = [
        evidence.model_dump(
            mode="json"
        )
        for evidence
        in result.evidence_records
    ]

    call_results_payload = [
        serialize_call_result(
            call_result
        )
        for call_result
        in result.call_results
    ]

    evidence_type_counts = {}

    oa_value_counts = {}

    for evidence in result.evidence_records:
        evidence_type = (
            evidence.evidence_type.value
        )

        evidence_type_counts[
            evidence_type
        ] = (
            evidence_type_counts.get(
                evidence_type,
                0,
            )
            + 1
        )

        if (
            evidence_type
            == "oa_status"
        ):
            oa_value = (
                evidence.value
                or "unknown"
            )

            oa_value_counts[
                oa_value
            ] = (
                oa_value_counts.get(
                    oa_value,
                    0,
                )
                + 1
            )

    summary = {
        "input_record_count": (
            len(
                access_records
            )
        ),
        "observed_date": (
            observed_date.isoformat()
        ),
        "delay_seconds": (
            DELAY_SECONDS
        ),
        "timeout_seconds": (
            TIMEOUT_SECONDS
        ),
        "attempted_calls": (
            result.attempted_calls
        ),
        "successful_calls": (
            result.successful_calls
        ),
        "failed_calls": (
            result.failed_calls
        ),
        "evidence_record_count": (
            len(
                result.evidence_records
            )
        ),
        "evidence_type_counts": (
            dict(
                sorted(
                    evidence_type_counts.items()
                )
            )
        ),
        "oa_value_counts": (
            dict(
                sorted(
                    oa_value_counts.items()
                )
            )
        ),
    }

    save_json(
        EVIDENCE_PATH,
        evidence_payload,
    )

    save_json(
        CALL_RESULTS_PATH,
        call_results_payload,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print()

    print(
        "RUN SUMMARY"
    )
    print(
        "-" * 120
    )

    print(
        f"attempted_calls="
        f"{result.attempted_calls}"
    )

    print(
        f"successful_calls="
        f"{result.successful_calls}"
    )

    print(
        f"failed_calls="
        f"{result.failed_calls}"
    )

    print(
        f"evidence_records="
        f"{len(result.evidence_records)}"
    )

    print()

    print(
        "EVIDENCE TYPE COUNTS"
    )
    print(
        "-" * 120
    )

    for (
        evidence_type,
        count,
    ) in sorted(
        evidence_type_counts.items()
    ):
        print(
            f"{evidence_type:<25} "
            f"{count}"
        )

    print()

    print(
        "OA STATUS COUNTS"
    )
    print(
        "-" * 120
    )

    for (
        oa_value,
        count,
    ) in sorted(
        oa_value_counts.items()
    ):
        print(
            f"{oa_value:<25} "
            f"{count}"
        )

    print()

    print(
        "FAILED CALLS"
    )
    print(
        "-" * 150
    )

    failed_results = [
        call_result
        for call_result
        in result.call_results
        if not call_result.success
    ]

    if not failed_results:
        print(
            "None"
        )

    for call_result in failed_results:
        print(
            f"{call_result.access_id:<12} "
            f"{call_result.candidate_id:<12} "
            f"{call_result.doi or '-':<35} "
            f"{call_result.error_type or '-'}: "
            f"{call_result.error_message or '-'}"
        )

    print(
        "-" * 150
    )

    print()

    print(
        "SAVED FILES"
    )
    print(
        "-" * 120
    )

    print(
        EVIDENCE_PATH.relative_to(
            PROJECT_ROOT
        )
    )

    print(
        CALL_RESULTS_PATH.relative_to(
            PROJECT_ROOT
        )
    )

    print(
        SUMMARY_PATH.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()


